from machine import Pin, time_pulse_us
import time

SOUND_SPEED=340 # The speed of sound
TRIG_PULSE_DURATION_US=10

trig_pin = Pin(0, Pin.OUT)
echo_pin = Pin(1, Pin.IN)

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