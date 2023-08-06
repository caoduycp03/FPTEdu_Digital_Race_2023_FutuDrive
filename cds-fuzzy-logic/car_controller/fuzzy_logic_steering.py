import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import sys
import pickle
from scipy import interpolate

sys.path.append(r'cds-fuzzy-logic\fuzzy_rule')
import read_rule as rr

V_SMALL = 'Very_Small'
SMALL = 'Small'
MEDIUM = 'Medium'
LARGE = 'Large'
V_LARGE = 'Very_Large'

#Fuzzification

#Antecedent
angle = ctrl.Antecedent(np.arange(0, 91, 1), 'angle')

angle[V_SMALL] = fuzz.trapmf(angle.universe, [0, 0, 10, 20])
angle[SMALL] = fuzz.trapmf(angle.universe, [10, 20, 30, 40])
angle[MEDIUM] = fuzz.trapmf(angle.universe, [30, 40, 50, 60])
angle[LARGE] = fuzz.trapmf(angle.universe, [50, 60, 70, 80])
angle[V_LARGE] = fuzz.trapmf(angle.universe, [70, 80, 90, 90])

#Consequent
steering = ctrl.Consequent(np.arange(0, 1.01, 0.01), 'steering')

steering[V_SMALL] = fuzz.trimf(steering.universe, [0, 0, 0])
steering[SMALL] = fuzz.trapmf(steering.universe, [0, 0.1, 0.3, 0.4])
steering[MEDIUM] = fuzz.trapmf(steering.universe, [0.3, 0.6, 0.6, 0.8])
steering[LARGE] = fuzz.trapmf(steering.universe, [0.6, 0.8, 1, 1])
steering[V_LARGE] = fuzz.trimf(steering.universe, [1, 1, 1])

#Create rule for inference
def steering_rule():
    rules = rr.read_steering_rule()
    steering_rules = []
    for item in rules:
        rule = ctrl.Rule(angle[item[0]], steering[item[1]])
        steering_rules.append(rule)
    return steering_rules

#Inference + Defuzzification to calculate steering
def defuzzify_steering(rule, angle_value):
    cmd_ctrl = ctrl.ControlSystem(rule)
    cmd_output = ctrl.ControlSystemSimulation(cmd_ctrl)
    cmd_output.input['angle'] = angle_value
    cmd_output.compute()
    return cmd_output.output['steering']

def create_steering_function(): #create a function for steering computing (less computation)
    x_values = np.arange(0, 91, 1)
    y_values = np.zeros(len(x_values))
    for i, x_value in enumerate(x_values):
        y_values[i] = defuzzify_steering(steering_rule(), x_value) 
    curve = interpolate.InterpolatedUnivariateSpline(x_values, y_values)
    return curve

def create_function(): #create re-usable function
    func = create_steering_function()
    with open (r'cds-fuzzy-logic\steering_func\steering_func.pkl', 'wb') as f: 
        pickle.dump(func, f)

if __name__ == '__main__':
    angle.view()
    plt.show()
    steering.view()
    plt.show()
    
    function1 = create_steering_function()

    create_function()
    
    x_values_plot = np.arange(0, 91, 1)
    y_values_plot = function1(x_values_plot)
    plt.plot(x_values_plot, y_values_plot)
    plt.show()   




