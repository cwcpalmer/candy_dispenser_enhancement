# Time to suffer gamers
# TODO
# Simulate communications with candycom over serial monitor - DONE
# Modify script to wait for a connection
# 
import time
import candycom #Letuce see what dis biotch can do
import asyncio
#import usb_cdc
candycomms = candycom.ClientComms()

async def main():
        await candycomms.comm_handler()

while True:
    asyncio.run(main())
