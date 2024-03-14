# candyserial Circuit Python Library ((ROUGH DRAFT))
# By Michael Lance
# 2/7/2024
# Updated 3/8/2024
#------------------------------------------------------------------------#
import sys
import serial 
import serial.tools.list_ports
import asyncio

#------------------------------------------------------------------------#
# Create function to determine the platform that the library is ran from
# and select an available Serial Port

def find_circuitpython_device():
    """Finds the serial port for an Arduino NRF52840 running CircuitPython
    
    :returns:
        The port name if found, None otherwise
    """
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "CircuitPython" in port.description or "NRF52840" in port.description:
            return port.device
    return None
#------------------------------------------------------------------------#


class usb_serial:
    def __init__(self, device='/dev/ttyACM1', baudrate=9600):
        if device is None:
            device = find_circuitpython_device()
            if device is None:
                print("No CircuitPython device found.")
                exit()
        self.ser = serial.Serial(device, baudrate, timeout=1)
        # Check if serial port is open
        if self.ser.is_open:
            print(f"Connected to {device} at {baudrate} baud.")
        else:
            print(f"Failed to open serial port {device}.")
            exit()

    def flush_ser_buffer(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def write(self, data):
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
        """Check if there's data waiting in the serial buffer."""
        return self.ser.in_waiting > 0