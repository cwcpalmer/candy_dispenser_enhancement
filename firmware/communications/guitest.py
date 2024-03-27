import tkinter as tk
import time
import candycom
import asyncio
from enum import Enum, auto

class ConnectionStates(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    DISCONNECTING = auto()
    
class MainGui():
    def __init__(self, loop):
        self.loop = loop
        self.keep_alive = True
        self.main_window = tk.Tk()
        self.main_window.title("Candy Machine Testing Application")
        self.main_window.geometry("800x600")
        self.ble_connection_state = ConnectionStates.DISCONNECTED
        self.usb_connection_state = ConnectionStates.DISCONNECTED
        self.status = tk.StringVar()
        self.status.set("")
        
        connection_container = tk.Frame(master=self.main_window)
        connection_container.pack(padx=10, pady=10)

        self.connect_ble_btn = tk.Button(master=connection_container, text="Connect ble", command=lambda: self.loop.create_task(self.connect_ble()))
        self.connect_ble_btn.pack(side=tk.LEFT, padx=10, pady=10)
        self.disconnect_ble_btn = tk.Button(master=connection_container, text="Disconnect ble", command=lambda: self.loop.create_task(self.disconnect_ble()))
        self.disconnect_ble_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.connect_usb_btn = tk.Button(master=connection_container, text="Connect USB", command=lambda: self.loop.create_task(self.connect_usb()))
        self.connect_usb_btn.pack(side=tk.LEFT, padx=10, pady=10)
        self.disconnect_usb_btn = tk.Button(master=connection_container, text="Disconnect USB", command=lambda: self.loop.create_task(self.disconnect_usb()))
        self.disconnect_usb_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # connection status
        status_container = tk.Frame(master=self.main_window)
        status_container.pack(padx=10, pady=10)
        self.status_lbl = tk.Label(master=status_container, textvariable=self.status)
        self.status_lbl.pack(padx=10, pady=10)

    def set_interface_state(self):
        if self.ble_connection_state is ConnectionStates.DISCONNECTED:
            self.connect_ble_btn["state"] = "normal"
            self.disconnect_ble_btn["state"] = "disabled"
        elif self.ble_connection_state is ConnectionStates.CONNECTING or self.ble_connection_state is ConnectionStates.DISCONNECTING:
            self.connect_usb_btn["state"] = "disabled"
            self.connect_ble_btn["state"] = "disabled"
            self.disconnect_ble_btn["state"] = "disabled"
        else:
            self.connect_ble_btn["state"] = "disabled"
            self.disconnect_ble_btn["state"] = "normal"
            
        if self.usb_connection_state is ConnectionStates.DISCONNECTED:
            self.connect_usb_btn["state"] = "normal"
            self.disconnect_usb_btn["state"] = "disabled"
        elif self.usb_connection_state is ConnectionStates.CONNECTING or self.usb_connection_state is ConnectionStates.DISCONNECTING:
            self.connect_usb_btn["state"] = "disabled"
            self.disconnect_usb_btn["state"] = "disabled"
        else:
            self.connect_usb_btn["state"] = "disabled"
            self.disconnect_usb_btn["state"] = "normal"
    
    async def connect_ble(self):
        self.ble_connection_state = ConnectionStates.CONNECTING
        self.comms = candycom.HostComms('ble')
        await self.comms.establish_connection()
        
    async def connect_usb(self):
        await self.comms.dispense_candy()
        print("connecting...")
        
    async def update(self):
        while self.keep_alive:
            self.main_window.update()
            self.set_interface_state()
            await asyncio.sleep(.1)
            
async def start_gui():
    gui = MainGui(asyncio.get_event_loop())
    await gui.update()
    await aysncio.sleep(.2)

if __name__ == '__main__':
    asyncio.run(start_gui())