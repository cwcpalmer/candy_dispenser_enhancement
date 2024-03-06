import candycom # Import the candycom library
import time
import asyncio

#TODO
# Send an ES command to start communications

candycomms = candycom.HostComms()

async def main():
    await candycomms.comm_handler()
    comamnd = input("send a command to the candy machine")
    candycomms.enqueue_message(comamnd)

while True:
    asyncio.run(main())
