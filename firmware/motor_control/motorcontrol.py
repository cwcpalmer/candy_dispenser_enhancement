# Experimental Stepper Motor Control Library for GIRRLS
# Written by Michael Lance
# 3/5/2024
# Updated: 3/14/2024
#------------------------------------------------------#

# Import Libraries needed to interact with micro controller
import board
from digitalio import DigitalInOut, Direction, Pull
import time
import asyncio

#------------------------------------------------------#

# Create Stepper Motor Class
class StepperMotor:
    def __init__(self):
        # Define GPIO Pins to interact with the beam breakers
        self.candy_dispensed = DigitalInOut(board.A0)
        self.candy_dispensed.direction = Direction.INPUT
        self.candy_dispensed.pull = Pull.UP

        # Define boolean to control whether or not candy has been dispensed2
        self.led = DigitalInOut(board.D3)
        self.led.direction = Direction.OUTPUT

        # Define GPIO Pins to interact with the stepper motor
        self.motor_pin_1 = DigitalInOut(board.D11)
        self.motor_pin_1.direction = Direction.OUTPUT
        self.motor_pin_1.value = False

        self.motor_pin_2 = DigitalInOut(board.D10)
        self.motor_pin_2.direction = Direction.OUTPUT
        self.motor_pin_2.value = False

        self.motor_pin_3 = DigitalInOut(board.D9)
        self.motor_pin_3.direction = Direction.OUTPUT
        self.motor_pin_3.value = False

        self.motor_pin_4 = DigitalInOut(board.D6)
        self.motor_pin_4.direction = Direction.OUTPUT
        self.motor_pin_4.value = False

        self.cur_step_index = 0
        self.successful_dispense = False

        self.steps = [
            [True, False, False, True],
            [True, True, False, False],
            [False, True, True, False],
            [False, False, True, True],  
        ]   
        self.motor_off = [False, False, False, False] # OFF

    async def rotate_motor(self):
        while not self.successful_dispense:
            for step_index in range(len(self.steps)):
                self.motor_pin_1.value = self.steps[step_index][0]
                self.motor_pin_2.value = self.steps[step_index][1]
                self.motor_pin_3.value = self.steps[step_index][2]
                self.motor_pin_4.value = self.steps[step_index][3]
                time.sleep(0.004)

            if self.candy_dispensed.value:
                self.led.value = False
            else:
                self.led.value = True
                self.successful_dispense = True

        self.motor_pin_1.value = self.motor_off[0] 
        self.motor_pin_2.value = self.motor_off[1]
        self.motor_pin_3.value = self.motor_off[2]
        self.motor_pin_4.value = self.motor_off[3]
        self.successful_dispense = False
        self.led.value = False
        return