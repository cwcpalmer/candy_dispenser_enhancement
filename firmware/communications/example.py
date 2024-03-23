import candycom # Import the candycom library
import time
import asyncio



Host = candycom.HostComms("ble")


async def main():
    await Host.establish_connection()
    while True:
        Host.dispense_candy()
        await asyncio.sleep(5)
asyncio.run(main())


