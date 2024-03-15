# Test of Candycom Library
# By Michael Lance
# 3/14/2024
#---------------------------------------------------------------------------------------------#
import candycom
import asyncio

candycomms = candycom.ClientComms("ble")

async def main():
    await candycomms.establish_connection()
    while True:
        await asyncio.sleep(0.05)


asyncio.run(main())
