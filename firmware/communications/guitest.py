# TODO: print the response in the log after recieving a response - Might be functional

import tkinter as tk
import time
import candycom

last_time = time.time()

log_entries = []

candycomms = candycom.HostComms()
candycom.determine_platform()

def connect_usb():
	add_to_log("Connect USB")
	"""
	establish = candycom.comm_dict["establish_connection"]
	candycomms.enqueue_message(establish)
	"""
	candycomms.establish_connection()
	return 

def connect_ble():
	add_to_log("Connect BLE")
	return

def dispense_candy():
	add_to_log("Request Dispense Candy")
	"""
	dispense = candycom.comm_dict["dispense_candy"]
	candycomms.enqueue_message(dispense)
	"""
	candycomms.dispense_candy()
	return

def get_battery_level():
	add_to_log("Getting Battery Level")
	return

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

def update_log_from_async(message):
	text_log.insert(tk.END, "Async: " + message + "\n")
	log_entries.append("Async: " + message + "\n")

def poll_messages():
	message = candycomms.receive_message()
	if message:
		update_log_from_async(message)
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