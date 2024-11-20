from machine import Pin, ADC, RTC
import time

import network
import socket
import struct

from ..Influx import Influx

rtc = RTC()

def set_time():
    # Get the external time reference
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo("pool.ntp.org", 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        print(s)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)

    except:
        print('[ERROR]')

    finally:
        s.close()

    #Set our internal time
    val = struct.unpack("!I", msg[40:44])[0]
    tm = val - 2208988800
    t = time.gmtime(tm)
    rtc.datetime((t[0],t[1],t[2],t[6]+1,t[3],t[4],t[5],0))
    print(t)
    print('Time synchronized')

set_time()

influx = Influx

while True:
    
    time.sleep(2)