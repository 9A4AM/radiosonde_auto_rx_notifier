import socket
import json
import random
import time
from datetime import datetime

# Configuration
UDP_IP = "127.0.0.1"  # Destination IP Address (localhost for testing)
UDP_PORT = 55673      # Destination Port

# Base payload template
BASE_PAYLOAD = {
    'type': 'PAYLOAD_SUMMARY',
    'station': 'CHANGEME',
    'callsign': 'V2850795',
    'latitude': 46.2590563,
    'longitude': 13.1551694,
    'altitude': 1001.84319,
    'speed': 72.185796,
    'heading': 124.94138,
    'time': '12:06:04',
    'comment': 'Radiosonde',
    'model': 'RS41-SG',
    'freq': '403.9990 MHz',
    'temp': -65.4,
    'frame': 6031,
    'bt': 65535,
    'humidity': 2.8,
    'pressure': -1,
    'sats': 9,
    'batt': 2.7,
    'snr': 11.3,
    'fest': [-2250.0, 2625.0],
    'f_centre': 403999187.5,
    'ppm': 98.77777777777777,
    'subtype': 'RS41-SG',
    'sdr_device_idx': '0',
    'vel_v': 5.62612,
    'vel_h': 20.05161
}

# Function to generate a dynamic payload based on the base template
def generate_dynamic_payload(base_payload):
    payload = base_payload
    payload['latitude'] += round(random.uniform(-0.001, 0.001), 5)  # Small latitude change
    payload['longitude'] += round(random.uniform(-0.001, 0.001), 5)  # Small longitude change
    payload['altitude'] -= round(random.uniform(50, 10), 2)  # Vary altitude slightly
    payload['speed'] += round(random.uniform(-2, 2), 2)  # Speed variation
    payload['heading'] = (payload['heading'] + random.uniform(-5, 5)) % 360  # Heading change
    payload['time'] = datetime.utcnow().strftime("%H:%M:%S")  # Update time
    payload['temp'] += round(random.uniform(-0.5, 0.5), 2)  # Temperature fluctuation
    payload['humidity'] = max(0, min(100, payload['humidity'] + random.uniform(-0.2, 0.2)))  # Humidity range
    payload['frame'] += 1  # Increment frame count
    payload['sats'] = random.randint(5, 12)  # Simulate number of satellites
    payload['batt'] = round(random.uniform(2.5, 4.2), 2)  # Battery voltage variation
    payload['snr'] += round(random.uniform(-0.5, 0.5), 2)  # SNR variation
    return payload

# Main function to send payloads over UDP
def main():
    print(f"Starting Radiosonde Telemetry Emulator - Sending to {UDP_IP}:{UDP_PORT}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        while True:
            dynamic_payload = generate_dynamic_payload(BASE_PAYLOAD)
            message = json.dumps(dynamic_payload)  # Convert payload to JSON string
            sock.sendto(message.encode('utf-8'), (UDP_IP, UDP_PORT))  # Send data
            print(f"Sent: {message}")
            time.sleep(1)  # Send data every second

    except KeyboardInterrupt:
        print("\nTelemetry Emulator stopped by user.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
