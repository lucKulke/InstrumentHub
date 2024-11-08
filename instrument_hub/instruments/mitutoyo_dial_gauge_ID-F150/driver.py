# instrument_driver.py (Python instrument data driver)
import sys
import time
import random
import evdev
import json
import time

# Path to the Mitutoyo device
DEVICE_PATH = "/dev/input/by-id/usb-Mitutoyo_USB-ITN_80093964-event-kbd"


# Mapping from key codes to corresponding numbers
KEY_MAPPING = {
    "KEY_KP1": "1",
    "KEY_KP2": "2",
    "KEY_KP3": "3",
    "KEY_KP4": "4",
    "KEY_KP5": "5",
    "KEY_KP6": "6",
    "KEY_KP7": "7",
    "KEY_KP8": "8",
    "KEY_KP9": "9",
    "KEY_KP0": "0",
    "KEY_KPDOT": ".",
    "KEY_ENTER": "",
    "KEY_NUMLOCK": "",
}


def listen() -> str:
    device = evdev.InputDevice(DEVICE_PATH)

    current_input = ""
    last_input = ""

    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            key_event = evdev.categorize(event)
            if key_event.keystate == evdev.KeyEvent.key_down:
                keycode = key_event.keycode
                if keycode in KEY_MAPPING:
                    current_input += KEY_MAPPING[keycode]
                    if keycode == "KEY_ENTER":
                        last_input = current_input
                        return last_input


def read_instrument_data():
    # Simulate reading data from an instrument (e.g., a USB device)
    return f"{random.random()}"


try:
    while True:
        data = listen()
        sys.stdout.write(data)
        sys.stdout.flush()  # Make sure data is sent immediately to stdout
        time.sleep(1)  # Simulate a delay in data collection (1 second)
except KeyboardInterrupt:
    print("Process interrupted")
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
