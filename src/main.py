import usb_hid
from adafruit_hid.gamepad import Gamepad

import time
import board
import digitalio
import analogio
import json
import os

# ======== config ========
dirty = False
loopDelay = 1/50
writeDelay = 50
potentiometerX = analogio.AnalogIn(board.GP26)
potentiometerY = analogio.AnalogIn(board.GP27)
led = digitalio.DigitalInOut(board.LED)

# ======== main program ========
print('Exec main')
print(os.listdir())

# read config
data = { 'border': 500, 'x': {'min': 65536,'center':0,'max':-65536}, 'y': {'min': 65536,'center':0,'max':-65536}}
try:
    with open('config.json', 'r') as configFile:        
        data = json.load(configFile)
except OSError:
    print('No config found. Configure center pos.')
    # determine center pos
    dirty = True
    for i in range(100):
        xc += potentiometerX.value
        yc += potentiometerY.value
        time.sleep(1/100)
    
    data['x']['center'] = int( xc / 100 )
    data['y']['center'] = int( yc / 100 )   

# read config structure
x1 = data['x']['min']
x2 = data['x']['max']
xc = data['x']['center']
xb = data['border']

y1 = data['x']['min']
y2 = data['y']['max']
yc = data['y']['center']
yb = data['border']

writeDelayCounter = writeDelay
gp = Gamepad(usb_hid.devices)
led.direction = digitalio.Direction.OUTPUT

def range_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# main loop
while True:
    isMoving = False
    # X
    valueX = potentiometerX.value
    gpX = 0
    
    if valueX < x1:
        x1 = valueX
        dirty = True
    if valueX > x2:
        x2 = valueX
        dirty = True
    
    if valueX < xc-xb:
        gpX = range_map(valueX, x1, xc, -127, 0)
        isMoving = True
    if valueX > xc+xb:
        gpX = range_map(valueX, xc, x2, 0, 127)
        isMoving = True

    # Y
    valueY = potentiometerY.value
    gpY = 0
    
    if valueY < y1:
        y1 = valueY
        dirty = True
    if valueY > y2:
        y2 = valueY
        dirty = True
    
    if valueY < yc-yb:
        gpY = range_map(valueY, y1, yc, -127, 0)
        isMoving = True
    if valueY > yc+yb:
        gpY = range_map(valueY, yc, y2, 0, 127)
        isMoving = True

    gp.move_joysticks(y=gpX, x=gpY, z=0)
    led.value = isMoving
    #gp.move_joysticks(x=gpX, y=gpY, z=0)
    
    # write config
    if writeDelayCounter > 0:
        writeDelayCounter = writeDelayCounter - 1
    
    if dirty==True and writeDelayCounter==0:
        
        dirty = False
        writeDelayCounter = writeDelay
        data = { 'border': xb, 'x': {'min': x1,'center':xc,'max':x2}, 'y': {'min': y1,'center':yc,'max':y2}}
        print('write new config')
        try:
            with open('config.json', 'w') as configFile:        
                data = json.dump(data,configFile)
        except OSError:
            print('Failed')
    
    # wait before next loop
    time.sleep(loopDelay)

