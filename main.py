from machine import ADC, Pin
import time
from Influx import Influx
import network

AIR_HUM = 57000
WATER_HUM = 150

hum_pin = 26
lamp_pins = [16, 17, 18]
pump_pin = 10

lamps = [Pin(lamp_pin, Pin.OUT) for lamp_pin in lamp_pins]
pump = Pin(pump_pin, Pin.OUT)
humidity_sensor = ADC(Pin(hum_pin, Pin.IN))

# Lamps always on
for lamp in lamps:
    lamp.value(1)
lamps[0].value(1)

influx = Influx()

# Main loop
while True:
    if not network.WLAN(network.STA_IF).isconnected():
        print("WiFi connection lost. Reconnecting...")
        influx.connect_to_wifi()

    raw_hum = humidity_sensor.read_u16()
    humidity = ((AIR_HUM - raw_hum) / AIR_HUM) * 100 # convert raw_hum to percentage
    print('raw_humidity: ' + str(raw_hum))
    print('humidity: ' + str(humidity))

    influx.send_data(raw_hum=humidity)

    if humidity <= 50:
        print('[INFO] Humidity might be too low')
        # Check if humidity is really too low
        hums = [raw_hum]
        for i in range(20):
            raw_hum = humidity_sensor.read_u16()
            hums.append(raw_hum)
            time.sleep(1)

        # Calculate avarage humidity
        avg_raw_hum = sum(hums)/20
        avg_humidity = ((AIR_HUM - avg_raw_hum) / AIR_HUM) * 100 # convert raw_hum to percentage

        if avg_humidity <= 50:
            print('[INFO] Humidity is too low')

            while humidity <= 60:
                pump.value(1)
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


    time.sleep(5)
    