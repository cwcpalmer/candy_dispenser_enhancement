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
    await candycomms.establish_connection()
    while True:
        if candycomms.IncommingBuffer.peek() == candycom.comm_dict["dispense_candy"]:
            candycomms.dequeue_message()

            testmotor.rotate_motor()
        elif candycomms.IncommingBuffer.peek() == "~ES":
            candycomms.dequeue_message()

        await asyncio.sleep(0.1) 
asyncio.run(main())