from machine import ADC, Pin, SoftI2C, RTC
import network

import time
from datetime import date

from Influx import Influx
from BH1750 import BH1750
from LCD import LCDScherm

AIR_HUM = 57000
WATER_HUM = 150

# Define pins
hum_pin = 26
lamp_pins = [16, 17, 18]
pump_pin = 10

# Initialize pins as INPUT or OUTPUT
lamps = [Pin(lamp_pin, Pin.OUT) for lamp_pin in lamp_pins]
pump = Pin(pump_pin, Pin.OUT)
humidity_sensor = ADC(Pin(hum_pin, Pin.IN))

rtc = RTC() # Initialize Real Time Clock

# Lamps always on for now
for lamp in lamps:
    lamp.value(1)

# Initialize I2C communication for light sensor
i2c_light = SoftI2C(scl=Pin(5), sda=Pin(4), freq=400000)

# Create BH1750 object
light_sensor = BH1750(bus=i2c_light, addr=0x23)
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

def check_lux(lux):
    if lux < 10:
        lamps[0].on()

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

    # manage_lamps()

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