# candyserial Circuit Python Library ((ROUGH DRAFT))
# By Michael Lance
# 2/7/2024
#------------------------------------------------------------------------#
import serial as serial

class usb_serial:
    def __init__(self, device='/dev/ttyACM1', baudrate=9600):
            device = '/dev/ttyACM1'
            baudrate = 9600 
            self.ser = serial.Serial(device, baudrate, timeout=1)
            # Check if serial port is open
            if self.ser.is_open:
                print(f"Connected to {device} at {baudrate} baud.")
            else:
                print(f"Failed to open serial port {device}")
                exit()
    def connect(self):
        print('hello world')


    def write(self, data):
        #print(type(data))
        if isinstance(data, str):
            data = data.encode('utf-8') 
        self.ser.write(data)

    
    def read(self, nbytes=32):
        """Read data from the USB serial connection."""
        data = self.ser.read(nbytes) 
        if data:
            return data.decode('utf-8') 
        return None 

    def check_ser_buffer(self):
        if self.ser.in_waiting > 3:
            return True
        else:
            return False