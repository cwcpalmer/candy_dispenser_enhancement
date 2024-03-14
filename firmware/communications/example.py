import candycom # Import the candycom library
import time
import asyncio

#TODO
# Send an ES command to start communications

Host = candycom.HostComms()


async def main():
    await Host.establish_connection()
    while True:
        Host.dispense_candy()
        await asyncio.sleep(5)
asyncio.run(main())


