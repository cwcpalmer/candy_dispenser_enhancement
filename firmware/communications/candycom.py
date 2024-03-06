# Asyncio based rewrite of candycom
# Written by Michael Lance
# 3/5/2024
#------------------------------------------------------------------------#

# import different libraries depending upon platform
import asyncio
import sys
import time

if sys.implementation.name != 'circuitpython':
    import candyserial
    usb_cdc = None # Used to appease the interpreter
elif sys.implementation.name == 'circuitpython':
    import usb_cdc
    candyserial = None  # Used to appease the interpreter

#------------------------------------------------------------------------#
# Create dictionaries to store command, event, and acks

comm_dict = {
    "establish_connection" : "~ES",
    "dispense_candy"       : "~ID",
    "reset_dispenser"      : "~QD",
}

evnt_dict = {
    "jam_or_empty"    : "%JP",
    "candy_taken"     : "%IR",
    "candy_dispensed" : "%MC"
}

ack_dict = {
    # Command Acks
    "~ES" : "@es", # Establish conenction ack
    "~ID" : "@iD", # Dispense candy ack
    "~QD" : "@qD", # Reset dispenser ack
    
    # Event Acks
    "%JP"   : "@jp", # Jam ack
    "%IR"   : "@ir", # Candy taken ack
    "%MC"   : "@mc"  # Candy dispensed ack


}

#------------------------------------------------------------------------#
# Create Circular Buffers to be used by each roles

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

    def if_data(self) -> bool:
        return not self.is_empty()

    def peek(self):
        if self.is_empty():
            return None  # Or raise an exception, based on your preference
        return self.buffer[self.start]

#------------------------------------------------------------------------#
# Create seperate classes for the two roles used by the protocal

class ClientComms: 
    def __init__(self, buffer_size=64):
        # Create two buffer instances
        self.IncommingBuffer = CircBuffer(buffer_size)
        self.OutgoingBuffer = CircBuffer(buffer_size)
        
        # Create flag management dict and total flag count
        self.is_connected = False 
        self.flag_count = 0
        self.client_flags = {
        "@jp": 0, # Jam flag
        "@ir": 0, # Candy taken flag
        "@mc": 0, # Candy dispensed flag
        #"report_battery_flag": 0
        }
        
    # Create methods for interacting with buffers

    def enqueue_message(self, message):
        self.OutgoingBuffer.enqueue(message)
    
    def dequeue_message(self):
        if self.IncommingBuffer.if_data():
            return self.IncommingBuffer.dequeue()

    
    def ser_buffer_if_data(self) -> bool:
        if usb_cdc.data.in_waiting >= 3:
            return True
        else:
            return False
    
    def outgoing_if_data(self) -> bool:
        return self.OutgoingBuffer.if_data()

    def incoming_if_data(self) -> bool:
        return self.IncommingBuffer.if_data()

    # Create async methods for transmitting data
    async def receive_message(self):
        self.IncommingBuffer.enqueue(usb_cdc.data.read(3).decode('utf-8')) 

    async def transmit_message(self): 
        usb_cdc.data.write(self.OutgoingBuffer.dequeue().encode('utf-8'))

    # Create Async Method to handle the connection
    async def establish_connection(self):
        while not self.is_connected:
            if self.ser_buffer_if_data():
                await self.receive_message()
                if self.incoming_if_data():
                    if self.dequeue_message() == comm_dict["establish_connection"]:
                        self.enqueue_message(ack_dict["~ES"])
                        await self.transmit_message()
                        self.is_connected = True
                        print("Connection Established")

    # Create async method used to handle communications
    async def comm_handler(self):
        if not self.is_connected:
            print("Waiting for Connection to be Established by Host...")
            await self.establish_connection()

        async def incoming_comm_handler():
            while self.ser_buffer_if_data():
                await self.receive_message()

        async def outgoing_comm_handler():
            while self.outgoing_if_data():
                await self.transmit_message()
        
        await asyncio.gather(
            incoming_comm_handler(),
            outgoing_comm_handler()
        )

        while self.flag_count > 0: # Flag handling for now
            checked_message = self.IncommingBuffer.peek()
            if checked_message in self.client_flags:
                self.client_flags_flags[checked_message] -= 1
                self.flag_count -= 1

class HostComms: 
    def __init__(self, buffer_size=64):
        # Create two buffer instances
        self.IncommingBuffer = CircBuffer(buffer_size)
        self.OutgoingBuffer = CircBuffer(buffer_size)
        self.candyser = candyserial.usb_serial()

        # Create flag management dict and total flag count
        self.is_connected = False 
        self.flag_count = 0
        self.host_flags = {
            "@es": 0, # Establish connection flag
            "@ir": 0, # Candy taken flag
            "@mc": 0, # Candy dispensed flag
        }
        
    # Create methods for interacting with buffers

    def enqueue_message(self, message):
        self.OutgoingBuffer.enqueue(message)
    
    def dequeue_message(self):
        if self.IncommingBuffer.if_data():
            return self.IncommingBuffer.dequeue()

    
    def ser_buffer_if_data(self) -> bool:
        return self.candyser.check_ser_buffer()
    
    def outgoing_if_data(self) -> bool:
        return self.OutgoingBuffer.if_data()

    def incoming_if_data(self) -> bool:
        return self.IncommingBuffer.if_data()

    # Create async methods for transmitting data
    async def receive_message(self):
        self.IncommingBuffer.enqueue(self.candyser.read(3)) 

    async def transmit_message(self): 
        self.candyser.write(self.OutgoingBuffer.dequeue())

    # Create Async Method to handle the connection
    async def establish_connection(self):
        while not self.is_connected:
            self.enqueue_message(comm_dict["establish_connection"])
            await asyncio.gather(
                self.transmit_message(),
                self.receive_message()
            )

            if self.dequeue_message() == ack_dict["~ES"]:
                self.is_connected = True
                print("Connection Established")
            
            await asyncio.sleep(1)

    # Create async method used to handle communications
    async def comm_handler(self):
        if not self.is_connected:
            print("Waiting for Connection to be Acknowledged by Client")
            await self.establish_connection()

        async def incoming_comm_handler():
            while self.ser_buffer_if_data():
                await self.receive_message()

        async def outgoing_comm_handler():
            while self.outgoing_if_data():
                await self.transmit_message()
        
        await asyncio.gather(
            incoming_comm_handler(),
            outgoing_comm_handler()
        )

        while self.flag_count > 0: # Flag handling for now
            checked_message = self.IncommingBuffer.peek()
            if checked_message in self.host_flags:
                self.host_flags[checked_message] -= 1
                self.flag_count -= 1
    