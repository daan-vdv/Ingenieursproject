from machine import Pin, ADC
import time

temp = ADC(Pin(27, Pin.IN))

while True:
    print(temp.read_u16())
    time.sleep(2)