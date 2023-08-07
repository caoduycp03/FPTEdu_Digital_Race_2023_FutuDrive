import asyncio
import base64
import json
import time
from io import BytesIO
from multiprocessing import Process, Queue
import cv2
import numpy as np
import websockets
from PIL import Image
from lane_line_detection import calculate_control_signal
from traffic_sign_detection import detect_sign, detect_distance
import pickle
from ultralytics import YOLO


###############################################################
config_path = 'config_param.json'
with open(config_path) as config_buffer:
    config = json.loads(config_buffer.read())

HEIGHT = config['general']['height']
WIDTH = config['general']['width']
WIDTH_SIGN = config['general']['width_sign']
HEIGHT_SIGN = config['general']['height_sign']
model_detect_sign_path = config['throttle_04']['model_detect_sign_path']
model_detect_sign = YOLO(model_detect_sign_path)
##############################################################

with open(r'cds_fuzzy_logic/speed_func/normal_throttle_func.pkl', 'rb') as f:
    speed_function = pickle.load(f)

with open(r'cds_fuzzy_logic/steering_func/steering_func.pkl', 'rb') as f:
    steering_function = pickle.load(f)

with open(r'cds_fuzzy_logic/speed_func/lr_sign_func.pkl', 'rb') as f:
    lr_sign_function = pickle.load(f)

with open(r'cds_fuzzy_logic/speed_func/object_func.pkl', 'rb') as f:
    object_function = pickle.load(f)

with open(r'cds_fuzzy_logic/speed_func/stop_sign_func.pkl', 'rb') as f:
    stop_sign_function = pickle.load(f)

with open(r'cds_fuzzy_logic/speed_func/straight_sign_func.pkl', 'rb') as f:
    straight_sign_function = pickle.load(f)



g_image_queue = Queue(maxsize=50)
sign_queue = Queue(maxsize=5)

def process_traffic_sign_loop(g_image_queue, sign_queue):
    while True:
        if g_image_queue.empty():
            time.sleep(0.1)
            continue
        image = g_image_queue.get()
        # Prepare visualization image
        draw = image.copy()
        # Detect traffic signs
        sign = detect_sign(image, model_detect_sign, draw=draw)
        if sign:
            if not sign_queue.full():
                sign_queue.put(sign)
        # Show the result to a window
        cv2.imshow("Traffic signs", draw)
        cv2.waitKey(1)

distance_lst = []
async def process_image(websocket, path):
    async for message in websocket:
        global distance_lst
        # Get image from simulation
        data = json.loads(message)
        image = Image.open(BytesIO(base64.b64decode(data["image"])))
        image = np.asarray(image)

        image_copy = image.copy().astype('float32')
        image_copy[:,:,0] -= 103.939
        image_copy[:,:,1] -= 116.779
        image_copy[:,:,2] -= 123.68
        image_lane = cv2.resize(image_copy, (WIDTH, HEIGHT))

        image_BGR = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image_sign = cv2.resize(image_BGR, (WIDTH_SIGN, HEIGHT_SIGN))

        # Prepare visualization image
        image = cv2.resize(image, (WIDTH, HEIGHT))
        draw = image.copy()


        # Update image to g_image_queue - used to run sign detection
        if not g_image_queue.full():
            g_image_queue.put(image_sign)

        if not sign_queue.empty():
            signs = sign_queue.get()
        else:
            signs = []

        # Send back throttle and steering angle
        # print("----------------------------", signs)
        angle = calculate_control_signal(image_lane, signs, draw=draw)
        
        if angle > 90:
            angle = angle - 90
            steering = - steering_function(angle).item()
        elif angle <= 90:
            angle = 90 - angle
            steering = steering_function(angle).item()

        throttle = speed_function(abs(steering)).item()

        if signs:
            sign = signs[-1][0]
            signs_pos = signs[-1][:]
            signs_pos.pop(0)
            car_pos = [WIDTH_SIGN/2, HEIGHT_SIGN]
            distance = detect_distance(signs_pos, car_pos, WIDTH_SIGN, HEIGHT_SIGN)
            distance_lst.append(distance)
            if distance <=0:
                distance_lst = []

            distance = distance - 5 / 100 - 5

            #Using steering and distance to determine throttle
            if signs[-1][0] == 'right' or signs[-1][0] == 'left':
                throttle = lr_sign_function(distance, steering).item()
            if signs[-1][0] == 'stop' or signs[-1][0] == 'no_entry':
                throttle = stop_sign_function(distance, steering).item()
            if signs[-1][0] == 'straight':
                throttle = straight_sign_function(distance, steering).item()

        if len(distance_lst) > 2 and distance_lst[-2] < distance_lst[-1]:
            distance_lst.pop(-1)


        cv2.imshow("draw", draw)
        cv2.waitKey(1)
        # Send back throttle and steering angle
        # throttle, steering_angle = 0,0
        message = json.dumps(
            {"throttle": throttle, "steering": steering})
        print(message)
        await websocket.send(message)

async def main():
    async with websockets.serve(process_image, "0.0.0.0", 4567, ping_interval=None):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    p = Process(target=process_traffic_sign_loop, args=(g_image_queue, sign_queue))
    p.start()
    asyncio.run(main())