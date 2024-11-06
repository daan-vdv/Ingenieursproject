from machine import ADC, Pin
import time

hum_pin = 26
adc = ADC(Pin(hum_pin))

while True:
    print(adc.read_u16())
    time.sleep(1)
    #43000 droog
    
    
