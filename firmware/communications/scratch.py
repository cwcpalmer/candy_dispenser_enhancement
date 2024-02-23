
if isinstance(message, dict):
    for value in message.values():
        self.OutgoingBuffer.enqueue(value)
elif isinstance(message, (list, tuple)):
    for item in message:
        self.OutgoingBuffer.enqueue(item)
else:
    self.OutgoingBuffer.enqueue(message)


# Open serial port
device = '/dev/ttyACM1'
baudrate = 9600 
self.ser = serial.Serial(device, baudrate, timeout=1)
# Check if serial port is open
if self.ser.is_open:
    print(f"Connected to {device} at {baudrate} baud.")
else:
    print(f"Failed to open serial port {device}")
    exit()


                
def write_serial(self):
    message = self.dequeue()
    if sys.implementation.name != 'circuitpython':
        com.ser.write(message.encode())
    else:
        usb_cdc.data.write(message.encode())

def read_serial(self):
    if usb_cdc.data.in_waiting > 0: #we can change this to 3 since we know we need 3 bytes
        self.enqueue(usb_cdc.data.read(usb_cdc.data.in_waiting))

"""
    In the Communications class, you're initializing a serial port (ser) within the __init__ method, 
    but you're not storing it as an instance variable. 
    You might want to store it if you plan to use it elsewhere in the class.

    In the CommBuffer.write_serial() method, 
    you're attempting to write data to usb_cdc.data. 
    However, it seems that usb_cdc doesn't have a data attribute. 
    You need to ensure that you have the correct method of accessing the USB CDC data stream.

    In the read_serial() method, you're using usb_cdc.data 
    to read data, but again, there's no guarantee that usb_cdc has a data attribute. 
    You need to ensure that you're using the correct method of accessing the USB CDC data stream.
    
    """

    """
    usb_cdc.data.write(b"Hello from CircuityPython\n")
    time.sleep(1)
    """


trans_constructor = {
    "Com" : "~",
    "Ack" : "@",
    "Evt" : "%",
    "EsCon" : "E",
    "rt1" : "I",
    "rtstp" : "D"
        }

        """
        while not self.is_connected:   
            self.comm_handler()
            if self.dequeue_message() == (ack_dict[connection_established]):
                print("Client Connected")
                self.is_connected = True
            time.sleep(1)
        """