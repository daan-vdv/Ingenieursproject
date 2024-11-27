import machine

sdaPIN=machine.Pin(8)  
sclPIN=machine.Pin(9)

i2c=machine.SoftI2C(sda=sdaPIN, scl=sclPIN, freq=100000)   

devices = i2c.scan()
print('14CORE - i2c Finder / Scanner ')
if len(devices) == 0:
 print("Error: No i2c device found, check properly the wiring!")
else:
 print('i2c devices found:',len(devices))
for device in devices:
 print("i2C Address: ",hex(device))