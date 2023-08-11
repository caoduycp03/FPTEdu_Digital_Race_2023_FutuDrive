import cv2
import numpy as np
import math
import torch

clas_list = ['unknown', 'right', 'left', 'straight', 'stop', 'no_entry', 'car']

def detect_sign(image, model, draw= None):
    signs = []
    cars = []
    results = model(image, verbose=False)
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            if box.conf[0] > 0.5:
                clas = box.cls[0]
                clas = clas_list[math.ceil(clas)]
                if clas == 'car':
                    cars.append([clas, x1, y1, x2-x1, y2-y1])
                else:   
                    signs.append([clas, x1, y1, x2-x1, y2-y1])
                    
                if draw is not None:
                    cv2.rectangle(draw, (x1,y1), (x2,y2), (0,255,0), 3)
                    cv2.putText(draw, clas + f" {str(round(float(box.conf[0]), 2))}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 3, cv2.LINE_AA)
    return signs, cars
    
    
def detect_distance(sign_position, car_position, width, height):
    origin_width = 640
    origin_height = 480
    
    sign_position = np.array(sign_position)
    car_position = np.array(car_position)
    longest_dis = 425
    shortest_dis = 379
    simulator_longest_dis = 80

    

    sign_position[0], sign_position[1] = (sign_position[0] *(origin_width/width)), (sign_position[1] *(origin_height/height))
    sign_position[2], sign_position[3] = (sign_position[2] *(origin_width/width)), (sign_position[3] *(origin_height/height))
    car_position[0], car_position[1] = (car_position[0] *(origin_width/width)), (car_position[1] *(origin_height/height))


    center_sign = [(sign_position[0] + sign_position[2])/2, (sign_position[1] + sign_position[3])/2]

    distance_2d = ((center_sign[0] - car_position[0])**2 + (center_sign[1] - car_position[1])**2)**(1/2)
    simulator_dis = simulator_longest_dis - simulator_longest_dis*((longest_dis-distance_2d)/(longest_dis-shortest_dis))
    return simulator_dis


def counter_car(signs_pos, width, height, number):
    
    print('1')
    if number == 'NO':
        return None, None, None
    if number == 'small':
        chosen_signs = signs_pos
        
    
    else: 
        print('bigger', signs_pos)
        chosen_signs = signs_pos[0]
        
        if signs_pos[1][2] > signs_pos[0][2]:
            chosen_signs  = signs_pos[1]
            
            

    print('final',chosen_signs)

    origin_width = 320
    origin_height = 240
    chosen_signs = np.array(chosen_signs)
    

    longest_dis = 170
    shortest_dis = 0
    simulator_longest_dis = 100


    chosen_signs[0], chosen_signs[1] = (chosen_signs[0] *float(origin_width/width)), (chosen_signs[1] *float(origin_height/height))
    chosen_signs[2], chosen_signs[3] = (chosen_signs[2] *float(origin_width/width)), (chosen_signs[3] *float(origin_height/height))

    right = False
    left = False
    
    #center_sign = [(chosen_signs[0] + chosen_signs[2])/2, (chosen_signs[1] + chosen_signs[3])/2]

    distance_2d = 100
    if chosen_signs[0] + chosen_signs[2]/2 < width/2:
        left = True
        if chosen_signs[0] > chosen_signs[2]:
            distance_2d = (((chosen_signs[0]-chosen_signs[2]))**2 + ((chosen_signs[1]-chosen_signs[3]))**2)**(1/2)
            
        else:
            distance_2d = chosen_signs[0]/2.5
          
        

    if chosen_signs[0] + chosen_signs[2]/2 > width/2:
        right = True
        distance_2d = ((chosen_signs[0] + chosen_signs[2] -290)**2 + ((chosen_signs[1]))**2)**(1/2)
        
       
    
    #simu_dis = simu_dis - simu_dis*(distance_2d/(longest_dis - shortest_dis))
    
    return distance_2d, right, left


