# raspberry_pi_simulation.py
import requests
import time
import random

INSTRUMENT_HUB_URL = "http://localhost:8000/instrument/send_data"

def send_weight_data():
    while True:
        # Simulate a random weight value
        weight = round(random.uniform(50.0, 100.0), 2)
        payload = {"data": weight, "name": "instrument1"}  # JSON format with correct field
        response = requests.post(INSTRUMENT_HUB_URL, json=payload)
        print(f"Sent weight: {weight} kg, Response: {response.json()}")
        time.sleep(5)  # Send data every 5 seconds


if __name__ == "__main__":
    send_weight_data()
