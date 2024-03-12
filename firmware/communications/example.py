import candycom # Import the candycom library
import time
import asyncio

#TODO
# Send an ES command to start communications

candycomms = candycom.HostComms()


async def main():
    await candycomms.establish_connection()
    while True:
        candycomms.enqueue_message("~ID")
        await asyncio.sleep(5)
asyncio.run(main())
