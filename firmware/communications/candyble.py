# BLE attempt at creating ble integration for candycom
# By Charles Palmer and Michael Lance
# 3/14/2024
# Updated 3/16/2024
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Import all libraries needed to interact with bluetooth low energy

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import board
import digitalio
import time
import sys

class BleClient():
    def __init__(self):
        self.ble = BLERadio()
        self.ble.name = "CANDYMAN"
        self.uart = UARTService()
        self.advertisement = ProvideServicesAdvertisement(self.uart)

        #self.connected_led = digitalio.DigitalInOut(board.BLUE_LED)
        #self.connected_led.direction = digitalio.Direction.OUTPUT 

        #self.pixel_shutoff = time.monotonic()
        #self.pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

    
        #self.connected_led.value = False

        self.ble.start_advertising(self.advertisement)
        while not self.ble.connected:    
            pass

    def write(self, data):
        data = data.encode('utf-8') 
        self.uart.write(data)

    def read(self):
        if self.uart.in_waiting >= 3:
            data = self.uart.read(3)
            
            return data.decode('utf-8')

class BleHost():
    def __init__(self):
        self.ble = BLERadio()
        self.uart_connection = None
        self.uart_service = None

        if not self.uart_connection:
            for adv in self.ble.start_scan(ProvideServicesAdvertisement):
                if UARTService in adv.services:
                    self.uart_connection = self.ble.connect(adv)
                    break
        self.ble.stop_scan()
        if self.uart_connection and self.uart_connection.connected:
            self.uart_service = self.uart_connection[UARTService]

    def write(self, data):
        data = data.encode('utf-8') 
        self.uart_service.write(data)

    def read(self):
        if self.uart_service.in_waiting >= 3:
            data = self.uart_service.read(3)
            
            return data.decode('utf-8')