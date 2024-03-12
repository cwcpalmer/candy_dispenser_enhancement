# Experimental Stepper Motor Control Library for GIRRLS
# Written by Michael Lance
# 3/5/2024
#------------------------------------------------------#

# Import Libraries needed to interact with micro controller
import board
from digitalio import DigitalInOut, Direction, Pull
import time

#------------------------------------------------------#

# Create Stepper Motor Class
class StepperMotor:
    def __init__(self):
        # Define GPIO Pins to interact with the stepper motor
        self.motor_pin_1 = DigitalInOut(board.D5)
        self.motor_pin_1.direction = Direction.OUTPUT
        self.motor_pin_1.value = False

        self.motor_pin_2 = DigitalInOut(board.D6)
        self.motor_pin_2.direction = Direction.OUTPUT
        self.motor_pin_2.value = False

        self.motor_pin_3 = DigitalInOut(board.D9)
        self.motor_pin_3.direction = Direction.OUTPUT
        self.motor_pin_3.value = False

        self.motor_pin_4 = DigitalInOut(board.D10)
        self.motor_pin_4.direction = Direction.OUTPUT
        self.motor_pin_4.value = False

        self.cur_step_index = 0


        self.steps = [
            [True, False, False, False],
            [False, True, False, False],
            [False, False, True, False],
            [False, False, False, True],
            [False, False, False, False] # OFF
        ]   

    def rotate_motor(self, num_steps=64):
            for rotation in range(num_steps):
                for step_index in range(len(self.steps)):
                    self.motor_pin_1.value = self.steps[step_index][0]
                    self.motor_pin_2.value = self.steps[step_index][1]
                    self.motor_pin_3.value = self.steps[step_index][2]
                    self.motor_pin_4.value = self.steps[step_index][3]
                    time.sleep(0.008)

            self.motor_pin_1.value = self.steps[4][0] 
            self.motor_pin_2.value = self.steps[4][1]
            self.motor_pin_3.value = self.steps[4][2]
            self.motor_pin_4.value = self.steps[4][3]
