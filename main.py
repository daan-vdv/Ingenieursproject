from machine import ADC, Pin, SoftI2C, RTC
import network
try:
    import usocket as socket
    import ustruct as struct
except:
    import socket
    import struct
import onewire, ds18x20

import time

from Influx import Influx
from BH1750 import BH1750
from LCD import LCDScherm

AIR_HUM = 57000
WATER_HUM = 150

# Define pins
hum_pin = 26
lamp_pins = [16, 17, 18]
pump_pin = 10
temp_pin = 22

# Initialize pins as INPUT or OUTPUT
lamps = [Pin(lamp_pin, Pin.OUT) for lamp_pin in lamp_pins]
pump = Pin(pump_pin, Pin.OUT)
humidity_sensor = ADC(Pin(hum_pin, Pin.IN))
temperatuur = Pin(temp_pin, Pin.IN)

rtc = RTC() # Initialize Real Time Clock

# Initialize I2C communication for light sensor
i2c = SoftI2C(sda=Pin(0), scl=Pin(1), freq=400000)

#Initialize LCD connection
lcd = LCDScherm()

# Create BH1750 object
light_sensor = BH1750(bus=i2c, addr=0x23)
light_sensor.reset()

#Initialize Influx connection
influx = Influx()

# Global variables for graphs
pump_value = 0
lamp_value = 0

def check_humidity(humidity, raw_hum):
    global pump_value

    if humidity <= 50:
        influx.log('Humidity might be too low', "INFO")
        # Check if humidity is really too low
        hums = [raw_hum]
        for _ in range(20):
            raw_hum = humidity_sensor.read_u16()
            hums.append(raw_hum)
            time.sleep(5)

        # Calculate avarage humidity
        avg_raw_hum = sum(hums)/20
        avg_humidity = ((AIR_HUM - avg_raw_hum) / AIR_HUM) * 100 # convert raw_hum to percentage

        if avg_humidity <= 50:
            influx.log('Humidity is too low', 'INFO')

            while humidity <= 60:
                pump.value(1)
                pump_value = 1
                time.sleep(5)
                pump.value(0)

                raw_hum = humidity_sensor.read_u16()
                humidity = ((AIR_HUM - raw_hum) / AIR_HUM) * 100 # convert raw_hum to percentage
                influx.log('raw_humidity: ' + str(raw_hum), 'DATA')
                influx.log('humidity: ' + str(humidity), 'DATA')

                time.sleep(5)

            pump.value(0)

        else:
            influx.log('Humidity is not too low.', 'INFO')

def set_time():
    # List of NTP servers and ports to try
    NTP_SERVERS = [
        ('ntp.UGent.be', 123),
    ]
    NTP_DELTA = 2208988800  # Seconds between 1900 and 1970
    
    # Connect to WiFi (replace with your credentials)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("IoTdevices", "zQDOj59FDAbgk8SOUhSo")
    
    # Wait for connection
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        influx.log('waiting for connection...', 'INFO')
        time.sleep(1)
        
    if wlan.status() != 3:
        raise RuntimeError('WiFi connection failed')
    else:
        influx.log('connected','INFO')
    
    # Create NTP request packet
    # Format is 48 bytes, first byte is 0x1B (00,011,011) for NTP version 3
    ntp_query = bytearray(48)
    ntp_query[0] = 0x1B
    
    # Try each server until one works
    for server, port in NTP_SERVERS:
        influx.log(f"Trying NTP server: {server}:{port}", 'INFO')
        try:
            addr = socket.getaddrinfo(server, port)[0][-1]
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2)  # Increased timeout
            
            try:
                s.sendto(ntp_query, addr)
                msg = s.recv(48)
                # If we get here, we succeeded
                influx.log(f"Success with {server}:{port}", 'INFO')
                
                # Extract time from response
                val = struct.unpack("!I", msg[40:44])[0]
                val -= NTP_DELTA
                
                # Update RTC
                tm = time.gmtime(val)
                rtc.datetime((tm[0], tm[1], tm[2], tm[6], tm[3]+1, tm[4], tm[5], 0))
                influx.log(f"RTC updated to: {time.localtime()}", 'INFO')
                return True
                
            except OSError as e:
                influx.log(f"Failed to get time from {server}:{port}: {str(e)}", 'ERROR')
                continue
                
            finally:
                s.close()
                
        except Exception as e:
            influx.log(f"Error with {server}:{port}: {str(e)}", 'ERROR')
            continue
    
    raise RuntimeError("Failed to get time from any NTP server")

def check_temp():
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(temperatuur))
    roms = ds_sensor.scan()
    ds_sensor.convert_temp()
    for rom in roms:
        tempC = ds_sensor.read_temp(rom)
    return tempC

def manage_lamps(lux):
    global lamp_value
    # Turn lamps off overnight based on hour
    t = time.localtime()
    current_hour = time.strftime('%H', t)

    # Turn on at 6u until 21u
    current_hour = int(current_hour)
    if current_hour < 21 and current_hour > 5:
        # Daytime, plant should get enough light
        # If not enough light and lights are not on, turn on lamps
        if lux < 15000:
            # influx.log('light level too low turning on lamps.', 'INFO')
            [lamp.on() for lamp in lamps]
            lamp_value = 1
    else:
        [lamp.off() for lamp in lamps]
        lamp_value = 0

# 0: Date
# 1: Humidity
# 2: Light Intensity
lcd_data_index = 0

set_time()

debiet_flag = 1
level_flag = 1

# Main loop
while True:
    pump_value = 0

    if not network.WLAN(network.STA_IF).isconnected():
        influx.log("WiFi connection lost. Reconnecting...", 'ERROR')
        influx.connect_to_wifi()
        


    tempC=check_temp()

    if lcd_data_index == 3:
        lcd_data_index = 0

    else:
        lcd_data_index += 1


    # Read humidity and convert to %
    raw_hum = humidity_sensor.read_u16()
    humidity = ((AIR_HUM - raw_hum) / AIR_HUM) * 100 # convert raw_hum to percentage

    lux = light_sensor.luminance(BH1750.CONT_HIRES_1)

    manage_lamps(lux)

    check_humidity(humidity, raw_hum)
    # check_lux(lux)

    datum = str(rtc.datetime()[0]) + '-' + str(rtc.datetime()[1]) + '-' + str(rtc.datetime()[2])

    all_data = [{"Datum": str(datum)}, {"Humidity %": humidity}, {"Lichthoeveelheid": str(lux) + " lux"}, {'Temperatuur': str(tempC) + 'C'}]
    data_to_show = list(all_data[lcd_data_index].keys())[0] 
    lcd.show_data(data_to_show, all_data[lcd_data_index][data_to_show])

    influx.send_data(hum=humidity, lux=lux, pump=pump_value, lights=lamp_value, temperature=tempC)
    time.sleep(5)