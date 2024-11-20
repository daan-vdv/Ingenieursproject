from machine import Pin
import time

pump = Pin(10, Pin.OUT)

pump.on()
time.sleep(2)
pump.off()
