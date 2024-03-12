# Asyncio based rewrite of candycom
# Written by Michael Lance & Thomas Baker
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
    # Commands
    "establish_connection" : "~ES",
    "dispense_candy"       : "~ID",
    "reset_dispenser"      : "~QD",
    "maintain_connection"  : "~RS",

    # Events
    "jam_or_empty"    : "%JP",
    "candy_taken"     : "%IR",
    "candy_dispensed" : "%MC"
}

ack_dict = {
    # Command Acks
    "~ES" : "@es", # Establish conenction ack
    "~ID" : "@iD", # Dispense candy ack
    "~QD" : "@qD", # Reset dispenser ack
    "~RS" : "@rs", # Maintain Connection Pulse
    
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

    def check_data(self) -> bool:
        return not self.is_empty()

    def peek(self):
        if self.is_empty():
            return None  
        return self.buffer[self.start]

    def flush(self):
        while not self.is_empty():
            print('removing from buffer')
            self.dequeue()


#------------------------------------------------------------------------#
# Create Class for the client side of the protocal

class ClientComms: 
    def __init__(self, buffer_size=64):
        # Create two buffer instances
        self.IncommingBuffer = CircBuffer(buffer_size)
        self.OutgoingBuffer = CircBuffer(buffer_size)
        # Create watchdog management variables
        self.watchdog_timeout = 64 # Roughly every half-second
        self.watchdog_timer = 0
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
    def check_data_on_serial(self) -> bool:
        if usb_cdc.data.in_waiting >= 3:
            return True
        else:
            return False
    
    def check_data_outgoing(self) -> bool:
        return self.OutgoingBuffer.check_data()

    def check_data_incoming(self) -> bool:
        return self.IncommingBuffer.check_data()

    def enqueue_message(self, message):
        # Set flag if the message is recognized format
        if message in comm_dict.values():
            self.client_flags[ack_dict[message]] += 1
            self.flag_count += 1
            self.OutgoingBuffer.enqueue(message)
        elif message in ack_dict.values():
            self.OutgoingBuffer.enqueue(message)
        else:
            print("Warning: Unrecognized message, nothing enqeued")

    def dequeue_message(self):
        if self.IncommingBuffer.check_data():
            message = self.IncommingBuffer.dequeue()
            if message in self.client_flags.keys():
                self.client_flags[message] -= 1
                self.flag_count -= 1
            if message in comm_dict.keys():
                self.enqueue_message(ack_dict[message])
            
            return message
 
    # Create async methods for transmitting data
    async def receive_message(self):
        message = usb_cdc.data.read(3).decode('utf-8')
        print(f'recieved: {message}')
        self.IncommingBuffer.enqueue(message) 

    async def transmit_message(self): 
        message = self.OutgoingBuffer.dequeue()
        print(f'transmitted: {message}') 
        usb_cdc.data.write(message.encode('utf-8'))

    # Create async watchdog method to maintain the connection
    async def connection_watchdog(self):
        print("running watchdog")
        while self.is_connected:
            if self.check_data_incoming():
                await self.receive_message()
                if self.IncommingBuffer.peek() == comm_dict["maintain_connection"]:
                    message = self.dequeue_message()
                    self.enqueue_message(ack_dict[message])
                    self.watchdog_timer = 0
                    print("resseting watchdog")

                else:
                    self.dequeue_message
                    self.watchdog_timer += 1
                    print("adding one to watchdog timer")
            else:
                self.watchdog_timer += 1
                print("adding one to watchdog timer")
        
            if self.watchdog_timer == self.watchdog_timeout:
                print("Conneciton Terminated by Watchdog Timeout")
                self.is_connected = False
                self.run_comm_handler.cancel()
                self.run_connection_watchdog.cancel()
                await self.establish_connection()
            await asyncio.sleep(1)
            print("watchdog operation complete")

    # Create async method used to handle communications
    async def comm_handler(self):
        print("running comm_handler")
        async def incoming_comm_handler():
            if self.check_data_on_serial():             
                await self.receive_message()
            else:
                await asyncio.sleep(1)

        async def outgoing_comm_handler():
            if self.check_data_outgoing():                
                await self.transmit_message()
            else:
                await asyncio.sleep(1)

        while self.is_connected:
            await asyncio.gather(
                incoming_comm_handler(),
                outgoing_comm_handler()
            )
    
    # Create async method to handle connection establishment
    async def establish_connection(self):
        print("Waiting for connection to be established")
        while not self.is_connected:
            if self.check_data_on_serial():
                await self.receive_message()
                if self.dequeue_message() == comm_dict["establish_connection"]:
                    self.enqueue_message(ack_dict["~ES"])
                    await self.transmit_message()
                    print("Connetion Established by host")
                    self.is_connected = True 
                    self.IncommingBuffer.flush()
            
            await asyncio.sleep(0.5)
        print("Connection Established")  
        # Run comm_handler and connection_watchdog as background tasks
        self.run_comm_handler = asyncio.create_task(self.comm_handler())
        self.run_connection_watchdog = asyncio.create_task(self.connection_watchdog())        


#------------------------------------------------------------------------#
# Create Class for the Host side of the protocal

class HostComms: 
    def __init__(self, buffer_size=64):
        # Create two buffer instances
        self.IncommingBuffer = CircBuffer(buffer_size)
        self.OutgoingBuffer = CircBuffer(buffer_size)
        self.candyser = candyserial.usb_serial()
        self.candyser.flush_ser_buffer()
        # Create watchdog management variables
        self.watchdog_timeout = 64
        self.watchdog_timer = 0
        # Create flag management dict and total flag count
        self.is_connected = False 
        self.flag_count = 0
        self.host_flags = {
            "@es": 0, # Establish connection flag
            "@ir": 0, # Candy taken flag
            "@mc": 0, # Candy dispensed flag
            "@rs": 0, # Maintain Conneciton flag
            "@iD": 0, # Candy Dispense flag
        }
        
    # Create methods for interacting with buffers
    def check_data_on_serial(self) -> bool:
        return self.candyser.check_ser_buffer()
    
    def check_data_outgoing(self) -> bool:
        return self.OutgoingBuffer.check_data()

    def check_data_incoming(self) -> bool:
        return self.IncommingBuffer.check_data()

    def enqueue_message(self, message):
        # Set flag if the message is recognized format
        if message in comm_dict.values():
            self.host_flags[ack_dict[message]] += 1
            self.flag_count += 1
            self.OutgoingBuffer.enqueue(message)
        elif message in ack_dict.values():
            self.OutgoingBuffer.enqueue(message)
        else:
            print("Warning: Unrecognized message, nothing enqeued")

    def dequeue_message(self):
        if self.IncommingBuffer.check_data():
            message = self.IncommingBuffer.dequeue()
            if message in self.host_flags.keys():
                self.host_flags[message] -= 1
                self.flag_count -= 1
            if message in comm_dict.keys():
                self.enqueue_message(ack_dict[message])
        return message
            

    # Create async methods for transmitting data
    async def receive_message(self):
        message = self.candyser.read(3)
        print(f'recieved: {message}')
        self.IncommingBuffer.enqueue(message) 

    async def transmit_message(self):
        message = self.OutgoingBuffer.dequeue()
        print(f'transmitted: {message}') 
        self.candyser.write(message)

    async def connection_watchdog(self):
        print("running watchdog")
        while self.is_connected:
            if self.check_data_incoming():
                self.dequeue_message()
                print("resetting watchdog")
                self.watchdog_timer = 0
            else:
                self.watchdog_timer += 1
                print("adding one to watchdog timer")
                self.enqueue_message(comm_dict["maintain_connection"])
                await self.transmit_message()
            if self.watchdog_timer == self.watchdog_timeout:
                print("Conneciton Terminated by Watchdog Timeout")
                self.is_connected = False
                self.run_comm_handler.cancel()
                self.run_connection_watchdog.cancel()
                await self.establish_connection()
            await asyncio.sleep(1)

    async def comm_handler(self):
        print("running comm_handler")
        async def incoming_comm_handler():
            if self.check_data_on_serial():
                await self.receive_message()
            else:
                await asyncio.sleep(1)

        async def outgoing_comm_handler():
            if self.check_data_outgoing():
                await self.transmit_message()
            else:
                await asyncio.sleep(1)
        while self.is_connected:
            await asyncio.gather(
                incoming_comm_handler(),
                outgoing_comm_handler()
            )  

    # Create Async Method to handle the connection
    async def establish_connection(self):
        print("attempting to establish connection")
        while not self.is_connected:
            self.enqueue_message(comm_dict["establish_connection"])     
            await self.transmit_message()
            if self.check_data_on_serial():
                print("message recieved")
                await self.receive_message()
                message = self.dequeue_message()
                print(message)
                if message == ack_dict["~ES"]:
                    print("Connection Established")
                    # Run comm_handler and connection_watchdog as background tasks
                    self.is_connected = True 
            await asyncio.sleep(1)
        print("Connection Established")     
        self.run_comm_handler = asyncio.create_task(self.comm_handler())
        self.run_connection_watchdog = asyncio.create_task(self.connection_watchdog())
        self.OutgoingBuffer.flush()
                    
               

