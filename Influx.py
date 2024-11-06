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
        super()


    # Send data to InfluxDB
    def send_data(self, raw_hum):
        # Construct the line protocol data
        data = f"raw_humidity value={raw_hum}"
        
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

        