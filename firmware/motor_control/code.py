import motorcontrol
import time

test_motor = motorcontrol.StepperMotor()
while True:
    test_motor.rotate_motor()
    time.sleep(5)