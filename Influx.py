import network
import time
import urequests
import ubinascii
import gc
import machine

class Influx:

    def __init__(self):
        self.INFLUXDB_URL = "http://194.164.125.152:8086/write?db=ip"
        self.INFLUXDB_USER = "ip"
        self.INFLUXDB_PASSWORD = "maindbIP"
        self.SSID = "IoTdevices"       # Replace with your WiFi SSID
        self.PASSWORD = "zQDOj59FDAbgk8SOUhSo"  # Replace with your WiFi password
        self.connect_to_wifi() # Connect to wifi when initialized
        self.led = machine.Pin("LED", machine.Pin.OUT)
        super()

    # Connect to WiFi
    def connect_to_wifi(self):
        wlan = network.WLAN(network.STA_IF)  # Set the network interface to station mode
        wlan.active(True)                    # Activate the network interface
        wlan.connect(self.SSID, self.PASSWORD)         # Connect to WiFi network
        
        # Wait for connection
        max_attempts = 10
        attempt_count = 0
        while not wlan.isconnected() and attempt_count < max_attempts:
            print("Connecting to WiFi...")
            time.sleep(1)
            attempt_count += 1
        
        if wlan.isconnected():
            print("Connected to WiFi!")
            print("Network config:", wlan.ifconfig())
        else:
            print("Failed to connect to WiFi.")

    # Send data to InfluxDB
    def send_data(self, hum, lux, pump, lights, temperature):
        self.led.on()
        # Construct the line protocol data
        data = f"raw_humidity value={hum}\nlux value={lux}\npump value={pump}\nlights value={lights}\ntempature value={temperature}"
        
        # Send the data with basic auth
        headers = {
            "Authorization": "Basic " + ubinascii.b2a_base64(f"{self.INFLUXDB_USER}:{self.INFLUXDB_PASSWORD}").decode().strip(),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            response = urequests.post(self.INFLUXDB_URL, headers=headers, data=data)
            if response.status_code == 204:
                print("Data written to InfluxDB successfully.")
            else:
                print("Failed to write data:", response.text)
            response.close()
        except Exception as e:
            print("Error writing to InfluxDB:", e)

        self.led.off()
