import candycom # Import the candycom library
import time

#TODO
# Send an ES command to start communications

candycomms = candycom.HostComms()

#candycomm.ser.write(b"~ES")


candycomms.establish_connection()
print('broke out of es loop')


while True:
    time.sleep(1)
    candycomms.dispense_candy()
    candycomms.comm_handler()