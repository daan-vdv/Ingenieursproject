from machine import I2C, Pin
from DIYables_MicroPython_LCD_I2C import LCD_I2C
import time
import math
import datetime

class LCDScherm:
    def __init__(self) -> None:
            
        # The I2C address of your LCD (Update if different)
        self.I2C_ADDR = 0x27  # Use the address found using the I2C scanner

        # Define the number of rows and columns on your LCD
        self.LCD_ROWS = 2
        self.LCD_COLS = 16

        # Initialize I2C
        self.i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

        # Initialize LCD
        self.lcd = LCD_I2C(self.i2c, self.I2C_ADDR, self.LCD_ROWS, self.LCD_COLS)

        # Setup function
        self.lcd.backlight_on()
        self.lcd.clear()

    def show_data(self, title, value):
        self.lcd.clear()
        start_pos = math.floor((16 - len(str(title))) /2)
        self.lcd.set_cursor(start_pos, 0)
        self.lcd.print(title)
        start_pos = math.floor((16 - len(str(value))) /2)
        self.lcd.set_cursor(start_pos, 1)
        self.lcd.print(str(value))
