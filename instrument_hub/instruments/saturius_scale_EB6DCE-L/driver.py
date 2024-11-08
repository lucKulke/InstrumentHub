import serial
import time
import sys
import multiprocessing

# Serial settings
DEVICE_PATH = "/dev/ttyUSB1"
BAUD_RATE = 9600
PARITY = serial.PARITY_ODD
STOPBITS = serial.STOPBITS_ONE
BYTESIZE = serial.SEVENBITS
TIMEOUT = 0.5  # seconds


# Function to listen for data from the scale
def listen(ser, command_queue):
    while True:
        # Check if there's a command in the queue to be sent
        if not command_queue.empty():
            command = command_queue.get()
            send_command(ser, command)  # Send the command

        # Now listen for data from the scale
        raw_data = ser.read(16)

        if raw_data:
            try:
                decoded_data = raw_data.decode("ascii", errors="ignore").strip()
                sys.stdout.write(decoded_data)
                sys.stdout.flush()  # Ensure immediate output
            except UnicodeDecodeError:
                sys.stdout.write("Error: Data decoding error")
                sys.stdout.flush()

        time.sleep(0.5)  # Polling interval


# Function to send a command to the scale
def send_command(ser, command_char):
    command = bytes([0x1B]) + command_char.encode() + bytes([0x0D, 0x0A])
    ser.write(command)
    # print(f"Sent command: {command_char}")


# Main function to initialize serial connection and handle commands
def main():
    command_queue = multiprocessing.Queue()

    # Open the serial connection
    with serial.Serial(
        DEVICE_PATH,
        BAUD_RATE,
        timeout=TIMEOUT,
        bytesize=BYTESIZE,
        parity=PARITY,
        stopbits=STOPBITS,
        rtscts=True,
    ) as ser:
        # Start the listener function in a separate process
        listener_process = multiprocessing.Process(
            target=listen, args=(ser, command_queue)
        )
        listener_process.start()

        while True:
            user_command = sys.stdin.readline().strip()
            if user_command == "Q":
                listener_process.terminate()
                break
            command_queue.put(user_command)


if __name__ == "__main__":
    main()
