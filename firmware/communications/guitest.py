import tkinter as tk
import time
import candycom
import asyncio

last_time = time.time()

log_entries = []

candycomms = None

def connect_usb():
    global candycomms
    add_to_log("Connect USB")
    candycomms = candycom.HostComms('serial')
    asyncio.run(candycomms.establish_connection())

def connect_ble():
    global candycomms
    add_to_log("Connect BLE")
    candycomms = candycom.HostComms('ble')
    asyncio.run(candycomms.establish_connection())

def dispense_candy():
    add_to_log("Request Dispense Candy")
    candycomms.enqueue_message("~ID")
    asyncio.run(candycomms.transmit_message())
    poll_messages()

def get_battery_level():
	add_to_log("Getting Battery Level")


def add_to_log(message):
	 global last_time, log_entries
	 cur_timestamp = time.time() 
	 gap_timestamp = cur_timestamp - last_time
	 text_log.insert( tk.END, f'{gap_timestamp:.3f}' + ": " + message + "\n")
	 log_entries.append(f'{gap_timestamp:.3f}' + ": " + message + "\n")
	 last_time = cur_timestamp

def save_log():
	print("Save log")
	with open("output_log.log", "w") as writer:
		for log_line in log_entries:
			writer.write(log_line)
	return

def poll_messages():
    asyncio.run(candycomms.receive_message())
    message = candycomms.dequeue_message()
    if message != None:
        if message == "@iD":
            add_to_log('Candy Dispensed')
    # Schedule poll_messages to be called again after 100 milliseconds
    main_window.after(100, poll_messages)


main_window = tk.Tk()
main_window.title("Candycomms communications tester 3000 rev 1.0.019, a Charles Palmer Product")
main_window.geometry("800x600")
main_window.configure(bg="hot pink")

# Connection container
connection_container = tk.Frame(master = main_window)
connection_container.pack(padx=10, pady=10)

usb_connect_btn = tk.Button(master = connection_container, text = "Connect USB", command=connect_usb)
usb_connect_btn.pack(side = tk.LEFT, padx = 10, pady = 10)
ble_connect_btn = tk.Button(master= connection_container, text="Connect BLE", command=connect_ble)
ble_connect_btn.pack(side = tk.LEFT, padx = 10, pady = 10)

# Actions container
action_container = tk.Frame(master = main_window)
action_container.pack(padx = 10, pady = 10)

dispense_candy_btn = tk.Button(master = action_container, text = "Dispense Candy", command=dispense_candy)
dispense_candy_btn.pack(side = tk.LEFT, padx = 10, pady = 10)
get_battery_level_btn = tk.Button(master = action_container, text = "Get Battery Level", command=get_battery_level)
get_battery_level_btn.pack(side = tk.LEFT, padx = 10, pady = 10)

# Log report
log_container = tk.Frame(master = main_window)
log_container.configure(bg="green")
log_container.pack(padx = 10, pady = 10)
text_log = tk.Text(master = log_container, width=100, height=24)
text_log.pack(padx = 10, pady = 10)
save_log_btn = tk.Button(master = log_container, text = "Save Log", command=save_log)
save_log_btn.pack(side = tk.RIGHT, padx = 10, pady = 10)



main_window.mainloop()