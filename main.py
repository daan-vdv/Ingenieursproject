from machine import ADC, Pin
import time
from Influx import Influx

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

influx = Influx()

# Main loop
while True:
    raw_hum = humidity_sensor.read_u16()
    humidity = ((AIR_HUM - raw_hum) / AIR_HUM) * 100 # convert raw_hum to percentage
    print('raw_humidity: ' + str(raw_hum))
    print('humidity: ' + str(humidity))

    influx.send_data(raw_hum=humidity)

    if humidity <= 60:
        while humidity <= 80:
            pump.value(1)

            raw_hum = humidity_sensor.read_u16()
            humidity = ((AIR_HUM - raw_hum) / AIR_HUM) * 100 # convert raw_hum to percentage

        pump.value(0)


    time.sleep(5)
    