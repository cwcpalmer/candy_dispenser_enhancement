import candycom # Import the candycom library
import time
import asyncio

#TODO
# Send an ES command to start communications

candycomms = candycom.HostComms()

async def send_input_command():
    comamnd = candycom.comm_dict["establish_connection"]
    candycomms.enqueue_message(comamnd)
async def main():
    await candycomms.comm_handler()
    await send_input_command()
    await asyncio.sleep(1)


while True:
    asyncio.run(main())
