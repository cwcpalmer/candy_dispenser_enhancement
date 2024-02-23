# Experimental attempt at creating circuit Python comms for GIRRLS project
# By Michael Lance & Thomas Baker
# Created: 02/06/2024
# Updated: 2/13/2024
#------------------------------------------------------------------------#
# TODO:
# Create BLE library to send messages from buffer
# Create ability for incoming and outgoing buffers to send data through candy serial
# Cretae establish connections method to send a ~ES and the corresponding ack ~es -Done

# Gracefully handle empty buffers

# import libraries used regardless of platform
import asyncio
import sys
import time

# import different libraries based on what platform the library is on
if sys.implementation.name != 'circuitpython':
    import candyserial
    usb_cdc = None # Used to appease the interpreter
elif sys.implementation.name == 'circuitpython':
    import usb_cdc
    candyserial = None  # Used to appease the interpreter

comm_dict = {
    "establish_connection" : "~ES",
    "dispense_candy"       : "~ID"
}

ack_dict = {
    "connection_established" : "@es",
    "candy_dispensed"        : "@id"
}

#------------------------------------------------------------------------#

class CircBuffer:
    def __init__(self, capacity: int):
        self.buffer = [None] * capacity
        self.capacity = capacity
        self.start = 0
        self.end = 0
        self.size = 0

    def is_full(self) -> bool:
        return self.size == self.capacity

    def is_empty(self) -> bool:
        return self.size == 0

    def enqueue(self, item):
        if self.is_full():
            print(f'Warning: Buffer Filled, Data Lost: {item}')
        self.buffer[self.end] = item
        self.end = (self.end + 1) % self.capacity
        self.size += 1

    def dequeue(self):
        if self.is_empty():
            return None
        item = self.buffer[self.start]
        self.buffer[self.start] = None 
        self.start = (self.start + 1) % self.capacity
        self.size -= 1
        return item

    def peek(self):
        if self.is_empty():
            return False
        return True
   
#------------------------------------------------------------------------#

class ClientComms: # Class used by client devices to communicate with usb_cdcor ble (indev)
    def __init__(self, buffer_size=64):
        self.IncommingBuffer = CircBuffer(buffer_size)
        self.OutgoingBuffer = CircBuffer(buffer_size)
            
    def enqueue_message(self, message): # Used to put a message in the buffer but not send it
        message1 = message
        self.OutgoingBuffer.enqueue(message1)
        #print("message enqueued")

    def dequeue_message(self): # Used to pull a message from the incoming buffer
        message = self.IncommingBuffer.dequeue()
        if message != None:
            return message

    def recieve_message(self): # Used for testing purposes    
        #print(f'3 Bytes Recieved: {usb_cdc.data.read(3)} of type {type(usb_cdc.data.read(3))}')
        self.IncommingBuffer.enqueue(usb_cdc.data.read(3).decode('utf-8')) 

    def transmit_message(self): # Used to send a message immediately, best used in an asyncio task
        message = self.OutgoingBuffer.dequeue()
        usb_cdc.data.write(message.encode('utf-8'))
        #print("message transmitted")

    def comm_handler(self):
        if self.OutgoingBuffer.peek():
            self.transmit_message()
        elif usb_cdc.data.in_waiting > 0: #we can change this to 3 since we know we need 3 bytes
            self.recieve_message()

    def establish_connection(self):
        is_connected = False # Flag used to mark if the client is connected or not
        while not is_connected:
            self.comm_handler()
            if self.dequeue_message() == comm_dict[establish_connection]:
                self.enqueue_message(ack_dict[connection_established])
                self.comm_handler()
                print("Host Connected")
                is_connected = True
        
    def interpret_command(self):
        command_recived = None
        while command_recived == None:
            message = self.recieve_message() # not using commhandler on purpose here
            if message == 
                
#------------------------------------------------------------------------#

class HostComms: # Class used by host devices to communicate over pyserial or ble (indev)
    def __init__(self, buffer_size=64):
        self.IncommingBuffer = CircBuffer(buffer_size)
        self.OutgoingBuffer = CircBuffer(buffer_size)
        self.com = candyserial.usb_serial()
        self.is_connected = False
        self.dispense_ack_expected = 0 # Flag raised when a command is sent 
            
    def enqueue_message(self, message): # Used to put a message in the buffer but not send it
        message = message
        self.OutgoingBuffer.enqueue(message)

    def dequeue_message(self): # Used to pull a message from the incoming buffer
        message = self.IncommingBuffer.dequeue()
        if message != None:
            return message

    def recieve_message(self): # Used for testing purposes
        message = self.com.read(3)
        if message:
            self.IncommingBuffer.enqueue(message)
        return None

    def transmit_message(self): # Used to send a message immediately, best used in an asyncio task
        #print("Attempting to dequeue message")
        message = self.OutgoingBuffer.dequeue()
        #print(f'Dequeued Message: {message}')
        self.com.write(message)

    def comm_handler(self):
        if self.OutgoingBuffer.peek():
            self.transmit_message()
        #elif self.com.check_ser_buffer(): #we can change this to 3 since we know we need 3 bytes
         #   print('you got mail')
        self.recieve_message()

    def establish_connection(self): # Used to establish a connection and await for confirmation
        self.enqueue_message(comm_dict['establish_connection'])
        self.comm_handler()
        
        

    def dispense_candy(self): 
        if not self.is_connected:
            print("Please establish connections and try again")
            return

        self.enqueue_message(comm_dict[dispense_candy])
        self.dispense_ack_expected += 1
       