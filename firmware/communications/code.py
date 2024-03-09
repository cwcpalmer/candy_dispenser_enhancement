# Test of Candycom Library
# By Michael Lance
# 3/6/2024
#---------------------------------------------------------------------------------------------#
import candycom
import motorcontrol
import asyncio


candycomms = candycom.ClientComms()
testmotor = motorcontrol.StepperMotor()

async def main():
    await candycomms.comm_handler()
    message = candycomms.dequeue_message()

    if message == candycom.comm_dict["dispense_candy"]:
        testmotor.rotate_motor()

while True:
    asyncio.run(main())