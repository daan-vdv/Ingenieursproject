from machine import ADC, Pin, SoftI2C, RTC, time_pulse_us
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
flow_pin = 6
clk_pin = 15
dt_pin = 14
sw_pin = 13


# Initialize pins as INPUT or OUTPUT
lamps = [Pin(lamp_pin, Pin.OUT) for lamp_pin in lamp_pins]
pump = Pin(pump_pin, Pin.OUT)
humidity_sensor = ADC(Pin(hum_pin, Pin.IN))
temperatuur = Pin(temp_pin, Pin.IN)
flow = Pin(flow_pin , Pin.IN, Pin.PULL_UP)

#Initialize flow sensor
global count
count = 0
callback = 0
def countPulse(channel):
   global count
   if start_counter == 1:
      count = count+1
 
flow.irq(countPulse)

rotary = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
dt_rotary = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
rotary_button = Pin(sw_pin, Pin.IN, Pin.PULL_UP)

def rotary_handler(pin):
    if rotary.value() == 0:
        update_lcd()

def give_water_on_press(pin):
    pump.on()
    time.sleep(3)
    pump.off()    

# Initialize rotary encoder
rotary.irq(trigger=Pin.IRQ_FALLING, handler=rotary_handler)
rotary_button.irq(trigger=Pin.IRQ_FALLING, handler=give_water_on_press)

rtc = RTC() # Initialize Real Time Clock

# Initialize I2C communication for light sensor
i2c = SoftI2C(sda=Pin(5), scl=Pin(4), freq=400000)

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

SOUND_SPEED=340 # The speed of sound
TRIG_PULSE_DURATION_US=10

trig_pin = Pin(19, Pin.OUT)
echo_pin = Pin(20, Pin.IN)

def get_water_volume():    #start distance sensor
    # Prepare the signal
    trig_pin.value(0)
    time.sleep_us(5)
    # Create an impulse of 10 µs
    trig_pin.value(1)
    time.sleep_us(TRIG_PULSE_DURATION_US)
    trig_pin.value(0)

    ultrason_duration = time_pulse_us(echo_pin, 1, 30000) # Receive the time the wave has travelled(in µs)
    distance_cm = SOUND_SPEED * ultrason_duration / 20000
    distance_cm = float(distance_cm)
    #end distance sensor
    
    
    #start formule volume
    h_gemeten = distance_cm
    h_extra_hoogte = 10.3
    h_gemeten -= h_extra_hoogte
    #print(h_gemeten)
    h_totaal_grotebak = 40.6    # start gegevens van de grote bak
    delta_h_grotebak = float(h_totaal_grotebak-h_gemeten)
    h_totaal_grotebak_inkeep = 36.6
    delta_h_grotebak_inkeep = float(h_totaal_grotebak_inkeep-h_gemeten)
    #print(delta_h_grotebak,delta_h_grotebak_inkeep)
    l_grote_bak = 49.6
    l_grote_bak_inkeep = 2.1
    b_top_grotebak = 38.7
    b_bottom_grotebak = 28.7
    b_top_inkeep = 8.1
    b_bottom_inkeep = 17.3 # end gegevens van de grote bak

    h_totaal_kleinebak = 12.7    # start gegevens van de kleine bak
    h_totaal_kleinebak_inkeep = 8.9
    #print(delta_h_grotebak,delta_h_grotebak_inkeep)
    l_kleinebak = 35.6
    l_kleinebak_inkeep = 1.4
    b_top_kleinebak = 27.5
    b_bottom_kleinebak = 23.5
    b_top_kleinebak_inkeep = 8.6
    b_bottom_kleine_inkeep = 10.2 # end gegevens van de kleine bak

    h_inkeep = 1.4  # start gegevens van inkeep tussen de kleine en de plantebak (2 kleine balkjes + 1 groter balkjes)
    b_grotebalk = 23.5
    l_grotebalk = 20.5
    b_kleine_balk = 10.5
    l_kleine_balk = 5.7

    h_totaal_plantbak = 26.3    # start gegevens van de plant bak
    h_totaal_plantbak_inkeep = 22.8
    #print(delta_h_grotebak,delta_h_grotebak_inkeep)
    l_plantbak = 34.1
    l_plantbak_inkeep = 1.2
    b_top_plantbak = 27.3
    b_bottom_plantbak = 21.2
    b_top_plantbak_inkeep = 9
    b_bottom_plantbak_inkeep = 12.1 # end gegevens van de plant bak

    h_totaal_klein_plant_balk= float(h_totaal_kleinebak + h_totaal_plantbak + h_inkeep)
    h_gemeten_extra =float(h_totaal_klein_plant_balk - h_gemeten)
    if h_gemeten_extra <= float(h_totaal_kleinebak) :
        delta_h = float(h_totaal_kleinebak-h_gemeten_extra)
        delta_h_inkeepbak = float(h_totaal_kleinebak_inkeep-h_gemeten_extra)
        if delta_h == 0:
            delta_h = h_totaal_kleinebak
        if delta_h_inkeepbak <= 0:
            delta_h_inkeepbak = h_totaal_kleinebak_inkeep

        v_bak = float((((delta_h* (b_bottom_kleinebak + b_top_kleinebak)) / 2) * l_kleinebak)-(2*(((delta_h_inkeepbak * (b_bottom_kleine_inkeep + b_top_kleinebak_inkeep)) / 2) * l_kleinebak_inkeep)))
        v_water = float((((delta_h_grotebak*(b_bottom_grotebak+b_top_grotebak))/2)*l_grote_bak)-(2*(((delta_h_grotebak_inkeep*(b_bottom_inkeep+b_top_inkeep))/2)*l_grote_bak_inkeep)) -v_bak)
  
  


    elif h_gemeten_extra <= float(h_totaal_kleinebak + h_inkeep):
        delta_h = float(h_inkeep - (h_gemeten_extra-h_totaal_kleinebak))
        if delta_h == 0:
            delta_h = h_inkeep
        v_bak = float((((h_totaal_kleinebak* (b_bottom_kleinebak + b_top_kleinebak)) / 2) * l_kleinebak)-(2*(((h_totaal_kleinebak_inkeep * (b_bottom_kleine_inkeep + b_top_kleinebak_inkeep)) / 2) * l_kleinebak_inkeep)))
        v_inkeep = float((b_grotebalk*l_grotebalk*delta_h) + (2*(b_kleine_balk*l_kleine_balk*delta_h)))
        v_water = float((((delta_h_grotebak*(b_bottom_grotebak+b_top_grotebak))/2)*l_grote_bak)-(2*(((delta_h_grotebak_inkeep*(b_bottom_inkeep+b_top_inkeep))/2)*l_grote_bak_inkeep)) -v_bak -v_inkeep)
    else:
        delta_h = float(h_totaal_plantbak - (h_gemeten_extra-h_totaal_kleinebak-h_inkeep))
        delta_h_inkeepbak =float(h_totaal_plantbak_inkeep -(h_gemeten_extra-h_totaal_kleinebak-h_inkeep))
        if delta_h == 0:
            delta_h = h_totaal_plantbak
        if delta_h_inkeepbak == 0:
            delta_h_inkeepbak = h_totaal_plantbak_inkeep
        v_bak = float((((h_totaal_kleinebak* (b_bottom_kleinebak + b_top_kleinebak)) / 2) * l_kleinebak)-(2*(((h_totaal_kleinebak_inkeep * (b_bottom_kleine_inkeep + b_top_kleinebak_inkeep)) / 2) * l_kleinebak_inkeep)))
        v_inkeep = float((b_grotebalk*l_grotebalk*h_inkeep) + (2*(b_kleine_balk*l_kleine_balk*h_inkeep)))
        v_bakplant = float((((delta_h* (b_bottom_plantbak + b_top_plantbak)) / 2) * l_plantbak)-(2*(((delta_h_inkeepbak * (b_bottom_plantbak_inkeep + b_top_plantbak_inkeep)) / 2) * l_plantbak_inkeep)))

        v_water = float((((delta_h_grotebak*(b_bottom_grotebak+b_top_grotebak))/2)*l_grote_bak)-(2*(((delta_h_grotebak_inkeep*(b_bottom_inkeep+b_top_inkeep))/2)*l_grote_bak_inkeep)) -v_bak -v_inkeep - v_bakplant)
    v_water = v_water/1000
    #end formule volume
    
    
    #start print
    print(f'{v_water} liter')
    return v_water
    #end print

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

            while humidity <= 60 and volume_flag == 1: # IF humidity is too low and debiet is fine
                pump.value(1)
                pump_value = 1
                time.sleep(2.5)
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
    max_wait = 20
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

def update_lcd():
    global lcd_data_index

    if lcd_data_index == 4:
        lcd_data_index = 0

    else:
        lcd_data_index += 1

    datum = str(rtc.datetime()[0]) + '-' + str(rtc.datetime()[1]) + '-' + str(rtc.datetime()[2])
    all_data = [{"Datum": str(datum)}, {"Humidity %": str(humidity) + ' %'}, {"Lichthoeveelheid": str(lux) + " lux"}, {'Temperatuur': str(tempC) + ' C'}, {'Water Voorraad': str(v_water) + ' L'}]
    data_to_show = list(all_data[lcd_data_index].keys())[0] 
    lcd.show_data(data_to_show, all_data[lcd_data_index][data_to_show])

# 0: Date
# 1: Humidity
# 2: Light Intensity
# 3: Temperature
# 4: Water volume
lcd_data_index = 0

set_time()

debiet_flag = 1
volume_flag = 1
level_flag = 1

# Main loop
while True:
    pump_value = 0

    if not network.WLAN(network.STA_IF).isconnected():
        influx.log("WiFi connection lost. Reconnecting...", 'ERROR')
        influx.connect_to_wifi()
        
    start_counter = 1
    time.sleep(1)
    start_counter = 0
    flow = (count / 7.5) # Pulse frequency (Hz) = 7.5Q, Q is flow rate in L/min.
    count = 0

    v_water = get_water_volume()

    if v_water < 5:
        influx.log(f'Water voorraad is bijna op! {v_water}', '[CRITICAL]')


    tempC=check_temp()

    # Read humidity and convert to %
    raw_hum = humidity_sensor.read_u16()
    humidity = ((AIR_HUM - raw_hum) / AIR_HUM) * 100 # convert raw_hum to percentage

    lux = light_sensor.luminance(BH1750.CONT_HIRES_1)

    manage_lamps(lux)

    check_humidity(humidity, raw_hum)
    # check_lux(lux)

    update_lcd()


    influx.send_data(hum=humidity, lux=lux, pump=pump_value, lights=lamp_value, temperature=tempC, flow=flow, v_water=v_water)
    time.sleep(5)