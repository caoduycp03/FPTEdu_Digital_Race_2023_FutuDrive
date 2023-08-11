import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import sys
import pickle
from scipy import interpolate

sys.path.append(r'cds_fuzzy_logic/fuzzy_rule')
import read_rule as rr


SMALL = 'Small'
MEDIUM = 'Medium'
BIG = 'Big'
NEAR = 'Near'
FAR = 'Far'
FAST = 'Fast'
SLOW = 'Slow'
STOP = 'Stop'

#Fuzzification

#Antecedent
dist = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'distance')
steering = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'steering')

dist[NEAR] = fuzz.trapmf(dist.universe, [0, 0, 0.3, 0.4])
dist[MEDIUM] = fuzz.trapmf(dist.universe, [0.3, 0.4, 0.6, 0.7])
dist[FAR] = fuzz.trapmf(dist.universe, [0.6, 0.7, 0.9, 1])
 
steering[SMALL] = fuzz.trapmf(steering.universe, [0, 0, 0.25, 0.5])
steering[MEDIUM] = fuzz.trapmf(steering.universe, [0.25, 0.5, 0.5, 0.75])
steering[BIG] = fuzz.trapmf(steering.universe, [0.5, 0.75, 1, 1])

#Consequent
speed = ctrl.Consequent(np.arange(0, 0.51, 0.01), 'speed')

speed[STOP] = fuzz.trimf(speed.universe, [0, 0, 0])
speed[SLOW] = fuzz.trapmf(speed.universe, [0, 0, 0.125, 0.25])
speed[MEDIUM] = fuzz.trapmf(speed.universe, [0.125, 0.25, 0.375, 0.5])
speed[FAST] = fuzz.trapmf(speed.universe, [0.375, 0.5, 0.5, 0.5])


#Create rule for inference
def throttle_rule():
    rules = rr.read_throttle_rule()
    throttle_rules = []
    for item in rules:
        rule = ctrl.Rule(steering[item[0]], speed[item[1]])
        throttle_rules.append(rule)
    return throttle_rules

def impediment_rule():
    rules = rr.read_impediment_rule()
    impediment_rules = []
    for item in rules:
        rule = ctrl.Rule(dist[item[0]] & steering[item[1]], speed[item[2]])
        impediment_rules.append(rule)
    return impediment_rules

def straight_rule():
    rules = rr.read_straight_rule()
    straight_rules = []
    for item in rules:
        rule = ctrl.Rule(dist[item[0]] & steering[item[1]], speed[item[2]])
        straight_rules.append(rule)
    return straight_rules

def stop_rule():
    rules = rr.read_stop_rule()
    stop_rules = []
    for item in rules:
        rule = ctrl.Rule(dist[item[0]] & steering[item[1]], speed[item[2]])
        stop_rules.append(rule)
    return stop_rules

def lr_rule():
    rules = rr.read_lr_rule()
    lr_rules = []
    for item in rules:
        rule = ctrl.Rule(dist[item[0]] & steering[item[1]], speed[item[2]])
        lr_rules.append(rule)
    return lr_rules

def noentry_rule():
    rules = rr.read_noentry_rule()
    noentry_rules = []
    for item in rules:
        rule = ctrl.Rule(dist[item[0]] & steering[item[1]], speed[item[2]])
        noentry_rules.append(rule)
    return noentry_rules

#Inference + Defuzzification to calculate speed
def defuzzify_speed(rule, steering_value, distance_value = None): # + dist_value
    cmd_ctrl = ctrl.ControlSystem(rule)
    cmd_output = ctrl.ControlSystemSimulation(cmd_ctrl)
    cmd_output.input['steering'] = steering_value
    if distance_value != None:
        cmd_output.input['distance'] = distance_value
    cmd_output.compute()
    return cmd_output.output['speed']

def create_speed_function(mode = 'normal_throttle'): #create a function for speed computing (less computation)
    x_values = np.arange(0, 1, 0.01)
    y_values = np.arange(0, 1, 0.01)
    z_values = np.zeros((len(x_values), len(y_values)))
    if mode == 'normal_throttle':
        z_values = np.zeros(len(x_values))
        for i, x_value in enumerate(x_values):
            z_values[i] = defuzzify_speed(throttle_rule(), x_value) 
        curve = interpolate.InterpolatedUnivariateSpline(x_values, z_values)
    if mode == 'object':
        for i, x_value in enumerate(x_values):
            for j, y_value in enumerate(y_values):
                z_values[i, j] = defuzzify_speed(impediment_rule(), x_value, y_value)
        curve = interpolate.RectBivariateSpline(x_values, y_values, z_values)
    if mode == 'straight_sign':
        for i, x_value in enumerate(x_values):
            for j, y_value in enumerate(y_values):
                z_values[i, j] = defuzzify_speed(straight_rule(), x_value, y_value)
        curve = interpolate.RectBivariateSpline(x_values, y_values, z_values)
    if mode == 'stop_sign':
        for i, x_value in enumerate(x_values):
            for j, y_value in enumerate(y_values):
                z_values[i, j] = defuzzify_speed(stop_rule(), x_value, y_value)
        curve = interpolate.RectBivariateSpline(x_values, y_values, z_values)
    if mode == 'lr_sign':
        for i, x_value in enumerate(x_values):
            for j, y_value in enumerate(y_values):
                z_values[i, j] = defuzzify_speed(lr_rule(), x_value, y_value)
        curve = interpolate.RectBivariateSpline(x_values, y_values, z_values)
    if mode == 'noentry_sign':
        for i, x_value in enumerate(x_values):
            for j, y_value in enumerate(y_values):
                z_values[i, j] = defuzzify_speed(noentry_rule(), x_value, y_value)
        curve = interpolate.RectBivariateSpline(x_values, y_values, z_values)
    return curve

def create_function(): #create re-usable function
    mode_list = ['normal_throttle', 'object', 'straight_sign', 'stop_sign', 'lr_sign', 'noentry_sign'] 
    for mode in mode_list:
        func = create_speed_function(mode)
        with open (f'cds_fuzzy_logic/speed_func/{mode}_func.pkl', 'wb') as f: 
            pickle.dump(func, f)

if __name__ == '__main__':
    # steering.view()
    # plt.show()
    # speed.view()
    # plt.show()
    # dist.view()
    # plt.show()
    
    # print(defuzzify_speed(lr_rule(), 0.8, 0.4))
    # print(defuzzify_speed(lr_rule(), 0.1, 0.5))

    # function1 = create_speed_function(mode='lr_sign')

    # print(function1(0.8, 0.4))
    # print(function1(0.1, 0.5))
        
    # with open(r'cds_fuzzy_logic/speed_func/stop_sign_func.pkl', 'rb') as f:
    #     stop_sign_function = pickle.load(f)

    # print(stop_sign_function(0,0.03))
    create_function()
    # print(lr_rule())    
    # x_values_plot = np.arange(0, 1.01, 0.01)
    # y_values_plot = np.arange(0, 1.01, 0.01)
    # z_values_plot = stop_sign_function(x_values_plot, y_values_plot)

    # plt.plot(z_values_plot)
    # plt.show()
    # x_values_plot = np.arange(0, 1.01, 0.01)
    # y_values_plot = function1(x_values_plot)
    # plt.plot(x_values_plot, y_values_plot)
    # plt.show()   




