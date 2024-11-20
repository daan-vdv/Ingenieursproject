from machine import ADC, Pin, SoftI2C, RTC
import network
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

# Lamps always on for now
for lamp in lamps:
    lamp.value(1)

# Initialize I2C communication for light sensor
i2c = SoftI2C(sda=Pin(0), scl=Pin(1), freq=400000)

# Create BH1750 object
light_sensor = BH1750(bus=i2c, addr=0x23)
light_sensor.reset()

#Initialize Influx connection
influx = Influx()

#Initialize LCD connection
lcd = LCDScherm()

# Global variables
pump_value = 0
lamp_value = 0

def check_humidity(humidity, raw_hum):
    global pump_value

    if humidity <= 50:
        print('[INFO] Humidity might be too low')
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
            print('[INFO] Humidity is too low')

            while humidity <= 60:
                pump.value(1)
                pump_value = 1
                time.sleep(5)
                pump.value(0)

                raw_hum = humidity_sensor.read_u16()
                humidity = ((AIR_HUM - raw_hum) / AIR_HUM) * 100 # convert raw_hum to percentage
                print('raw_humidity: ' + str(raw_hum))
                print('humidity: ' + str(humidity))

                time.sleep(5)

            pump.value(0)

        else:
            print('[INFO] Humidity is not too low.')

def set_time():
    # Get the external time reference
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo("pool.ntp.org", 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        print(s)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)

    except:
        print('[ERROR]')

    finally:
        s.close()

    #Set our internal time
    val = struct.unpack("!I", msg[40:44])[0]
    tm = val - 2208988800
    t = time.gmtime(tm)
    rtc.datetime((t[0],t[1],t[2],t[6]+1,t[3],t[4],t[5],0))
    print(t)
    print('Time synchronized')

def check_lux(lux):
    if lux < 10:
        lamps[0].on()

def check_temp():
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(temperatuur))

    roms = ds_sensor.scan()
    print('Found DS devices: ', roms)

    while True:
      ds_sensor.convert_temp()
      time.sleep_ms(750)
      for rom in roms:
        print(rom)
        tempC = ds_sensor.read_temp(rom)
        print('temperature (ºC):', "{:.2f}".format(tempC))
        print()
      time.sleep(5)

def manage_lamps():
    global lamp_value
    # Turn lamps off overnight based on hour
    t = time.localtime()
    current_hour = time.strftime('%H', t)
    print(current_hour)
    # Turn on at 6u until 21u
    current_hour = int(current_hour)
    if current_hour < 20 and current_hour > 5:
        [lamp.on() for lamp in lamps]
        lamp_value = 1

    else:
        [lamp.off() for lamp in lamps]
        lamp_value = 0

# 0: Date
# 1: Humidity
# 2: Light Intensity
lcd_data_index = 0

# Main loop
while True:
    pump_value = 0
    set_time()

    manage_lamps()

    if lcd_data_index == 2:
        lcd_data_index = 0

    else:
        lcd_data_index += 1

    if not network.WLAN(network.STA_IF).isconnected():
        print("WiFi connection lost. Reconnecting...")
        influx.connect_to_wifi()

    # Read humidity and convert to %
    raw_hum = humidity_sensor.read_u16()
    humidity = ((AIR_HUM - raw_hum) / AIR_HUM) * 100 # convert raw_hum to percentage

    lux = light_sensor.luminance(BH1750.CONT_HIRES_1)


    check_humidity(humidity, raw_hum)
    check_lux(lux)

    datum = str(rtc.datetime()[0]) + '-' + str(rtc.datetime()[1]) + '-' + str(rtc.datetime()[2])

    all_data = [{"Datum": str(datum)}, {"Humidity %": humidity}, {"Lichthoeveelheid": str(lux) + " lux"}]
    data_to_show = list(all_data[lcd_data_index].keys())[0] 
    lcd.show_data(data_to_show, all_data[lcd_data_index][data_to_show])

    influx.send_data(hum=humidity, lux=lux, pump=pump_value, lights=lamp_value)
    time.sleep(5)