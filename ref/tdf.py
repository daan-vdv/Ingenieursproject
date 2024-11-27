from machine import Timer

display = ['jkdsf', 'jsdkf']
lcd_index = 0

timer = Timer()

def increment_lcd():
    global lcd_index
    lcd_index += 1



timer.init()