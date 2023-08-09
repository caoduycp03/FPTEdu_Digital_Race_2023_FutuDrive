import cv2
import numpy as np
import time
import threading
import json
import math
import statistics as st
###############################################################
config_path = 'config_param.json'
with open(config_path) as config_buffer:
    config = json.loads(config_buffer.read())

HEIGHT = config['general']['height']
WIDTH = config['general']['width']
config_throttle = "throttle_04"
THROTTLE = config[config_throttle]['throttle']
MODEL_PATH = config[config_throttle]['model_onnx_path']
# model = tf.keras.models.load_model(MODEL_PATH, compile= False)
print(MODEL_PATH)
model = cv2.dnn.readNetFromONNX(MODEL_PATH)
##############################################################

def birdview_transform(img):
    a = 25
    b = 25
    src = np.float32([[0, HEIGHT//2.5], [WIDTH+0, HEIGHT//2.5], [0, HEIGHT-40], [WIDTH, HEIGHT-40]])
    dst = np.float32([[-a, 0], [WIDTH + a, 0], [b, HEIGHT], [WIDTH-b, HEIGHT]])
    M = cv2.getPerspectiveTransform(src, dst) # The transformation matrix
    warped_img = cv2.warpPerspective(img, M, (WIDTH, HEIGHT)) # Image warping
    return warped_img

def find_left_right_points(roi, image, draw=None):
    # Consider the position 70% from the top of the image
    interested_line_y = int(HEIGHT * roi)
    if draw is not None:
        cv2.line(draw, (0, interested_line_y),
                 (WIDTH, interested_line_y), (0, 0, 255), 2)
    interested_line = image[interested_line_y, :]

    # Detect left/right points
    left_point = -1
    right_point = -1
    lane_width = 48
    center = WIDTH // 2

    for x in range(0, WIDTH, 1):
        if interested_line[x] == 1:
            left_point = x
            break
    for x in range(WIDTH-1, 0, -1):
        if interested_line[x] == 1:
            right_point = x
            break
    '''this end point method apply for 128x128 images, if the height of new image is different
        multiply the end point with new_height/last_height'''
    
    end_point = (68 - (HEIGHT - interested_line_y))/(68 - 0.2*HEIGHT) *17
    if left_point < end_point and right_point != -1:
        left_point = left_point - ((WIDTH/2) - (right_point - left_point) )

    if right_point > (128 - end_point) and left_point != -1:
        right_point = right_point + ((WIDTH/2) - (right_point - left_point) )

    if draw is not None:
        if left_point != -1:
            draw = cv2.circle(
                draw, (int(left_point), interested_line_y), 3, (255, 255, 0), -1)
        if right_point != -1:
            draw = cv2.circle(
                draw, (int(right_point), interested_line_y), 3, (0, 255, 0), -1)

    return left_point, right_point

pred = 0
def detect_lane_model(model, img):
    global pred
    # img = cv2.equalizeHist(img.astype('float32'))
    model.setInput(img.reshape(1, HEIGHT, WIDTH, 3))
    pred = model.forward()
    pred = pred[:,:,:,1:2].reshape(HEIGHT, WIDTH, 1)

    # pred = model.predict(img.reshape(1, HEIGHT, WIDTH, 3))
    # pred = pred[:,:,:,1:2].reshape(HEIGHT, WIDTH, 1)
    pred[pred >= 0.5] = 1
    pred[pred < 0.5] = 0

time_to_turn = False
check_distance = False
sign_list = []

sign = "hello"
angle_turn = 90
def calculate_control_signal(img, signs, cars, distance, draw=None):
    global pred, angle_turn, time_to_turn, sign, sign_list, check_distance

    #################### predict
    detect_lane = threading.Thread(target=detect_lane_model, args= (model, img))
    detect_lane.start()
    ####################

    pred_birdview = birdview_transform(pred)
    cv2.imshow("pred_birdview", pred_birdview)
    cv2.waitKey(1)
    draw[:, :] = birdview_transform(draw)
    left_point, right_point = find_left_right_points(0.7, pred_birdview, draw=draw)
    left_point_2, right_point_2 = find_left_right_points(0.55, pred_birdview, draw=draw)
    left_point_3, right_point_3 = find_left_right_points(0.9, pred_birdview, draw=draw)
    lane_width = 42
    angle_degrees = 90
############### control when detect sign
    if signs:
        sign = signs[-1][0]
        sign_list.append(sign)
        if st.mode(sign_list) == 'left':
            angle_turn = 145
        if st.mode(sign_list) == 'right':
            angle_turn = 35
    
    print(distance)
    if distance:
        if distance <= 50:
            check_distance = True

    if len(sign_list) > 0:   
        print(st.mode(sign_list)) 
        if (st.mode(sign_list) == 'left' and left_point_2 - left_point > 5) or (st.mode(sign_list) == 'right' and right_point_2 - right_point > 5):
            print('duy pro')
            if check_distance:
                time_to_turn = True
    


    if time_to_turn and abs(right_point - left_point) <= lane_width and abs(right_point_2 - left_point_2) <= lane_width and abs(left_point_3 - right_point_3) <= lane_width:
    #abs(np.sum(pred_birdview[:,:WIDTH//2-1]) - np.sum(pred_birdview[:,WIDTH//2:WIDTH-1])) < 20: 
        print('duy dep trai')
        print(abs(right_point - left_point))
        print(abs(right_point_2 - left_point_2))
        print(abs(left_point_3 - right_point_3))
        time_to_turn = False
        check_distance = False
        sign_list = []
        angle_turn = 90

    if time_to_turn and check_distance:
        print(angle_turn)
        print(abs(right_point - left_point))
        print(abs(right_point_2 - left_point_2))
        print(abs(left_point_3 - right_point_3))
        return angle_turn
###############

    if left_point != -1 and right_point != -1:
        x1, x2 = left_point, right_point
        middle_of_road = ((x1 + x2) / 2, HEIGHT * 0.7)
        x3, y3 = middle_of_road
        middle_point = (WIDTH//2, HEIGHT)
        x4, y4 = middle_point
        if x3 - x4 == 0:
            angle_degrees = 90
        else:
            slope = (y4 - y3) / (x3 - x4)
            angle_radians = math.atan(slope)
            if x3 - x4 > 0:
                angle_degrees = math.degrees(angle_radians)
            else:
                angle_degrees  = math.degrees(angle_radians) + 180
    return angle_degrees















