import os
import machine

class Influx:
    __ip = os.environ['IP']
    __password = os.environ['PASSWORD']
    __humidity_pin = 26
    __light_pin = 0
    __current_pin = 0

    def __init__(self):
        super()

    def send_data(self):
        # Vochtigheid

        # Temperatuur
        # licht
        # stroom
        # Debiet
        # Waterniveau
        pass
    