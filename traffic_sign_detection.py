import cv2
import numpy as np
import math

clas_list = ['unknown', 'right', 'left', 'straight', 'stop', 'no_entry']

def detect_sign(image, model, draw= None):
    signs = []
    results = model(image, verbose=False)
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            if box.conf[0] > 0:
                clas = box.cls[0]
                clas = clas_list[math.ceil(clas)]
                signs.append([clas, x1, y1, x2-x1, y2-y1])
                if draw is not None:
                    cv2.rectangle(draw, (x1,y1), (x2,y2), (0,255,0), 3)
                    cv2.putText(draw, clas, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3, cv2.LINE_AA)

    return signs
    
    
def detect_distance(sign_position, car_position, width, height):
    origin_width = 640
    origin_height = 480
    
    sign_position = np.array(sign_position)
    car_position = np.array(car_position)
    longest_dis = 418.67
    shortest_dis = 379
    simulator_longest_dis = 80

    

    sign_position[0], sign_position[1] = (sign_position[0] *(origin_width/width)), (sign_position[1] *(origin_height/height))
    sign_position[2], sign_position[3] = (sign_position[2] *(origin_width/width)), (sign_position[3] *(origin_height/height))
    car_position[0], car_position[1] = (car_position[0] *(origin_width/width)), (car_position[1] *(origin_height/height))


    center_sign = [(sign_position[0] + sign_position[2])/2, (sign_position[1] + sign_position[3])/2]

    distance_2d = ((center_sign[0] - car_position[0])**2 + (center_sign[1] - car_position[1])**2)**(1/2)
    simulator_dis = simulator_longest_dis - simulator_longest_dis*((longest_dis-distance_2d)/(longest_dis-shortest_dis))
    return simulator_dis