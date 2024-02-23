# Time to suffer gamers
# TODO
# Simulate communications with candycom over serial monitor - DONE
# Modify script to wait for a connection
# 
import time
import candycom #Letuce see what dis biotch can do
#import usb_cdc
candycomms = candycom.ClientComms()

candycomms.establish_connection()
print('broke out of es loop')

while True:
    time.sleep(1)
    candycomms.comm_handler()
    message_recieved = candycomms.dequeue_message()
    if message_recieved == '~ID':
        candycomms.enqueue_message('~id')
        candycomms.comm_handler()

        print(message_recieved)


