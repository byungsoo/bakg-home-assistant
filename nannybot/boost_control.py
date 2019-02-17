#!/usr/bin/env python3
import pdb
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import time
import os
import subprocess
from random import randint
from picamera import PiCamera
from time import sleep

from pyb00st.movehub import MoveHub
from pyb00st.constants import *
from time import sleep

MY_MOVEHUB_ADD = '00:16:53:A1:6F:4F'
MY_BTCTRLR_HCI = 'hci0'

mymovehub = MoveHub(MY_MOVEHUB_ADD, 'BlueZ', MY_BTCTRLR_HCI)
mymovehub.start()
mymovehub.subscribe_all()
mymovehub.listen_hubtilt(MODE_HUBTILT_BASIC)
mymovehub.listen_colordist_sensor(PORT_D)
    
if mymovehub.is_connected():
    print(('Is connected: ', mymovehub.is_connected()))

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_PATH_SS)

UNIT_MOVE_MSEC = 100
UNIT_MOVE_POWER = 100

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    # pdb.set_trace()
    try:
        cmd = json.loads(msg.payload.decode())
        print(cmd)
        if cmd['dir'] == 'left':
            mymovehub.run_motor_for_time(MOTOR_B, int(cmd['time']*UNIT_MOVE_MSEC), UNIT_MOVE_POWER)
        elif cmd['dir'] == 'right':
            mymovehub.run_motor_for_time(MOTOR_A, int(cmd['time']*UNIT_MOVE_MSEC), UNIT_MOVE_POWER)
        elif cmd['dir'] == 'front':
            mymovehub.run_motor_for_time(MOTOR_AB, int(cmd['time']*UNIT_MOVE_MSEC), UNIT_MOVE_POWER)
        elif msg.payload == b'move front':
            mymovehub.run_motor_for_time(MOTOR_AB, UNIT_MOVE_MSEC, UNIT_MOVE_POWER)
        elif msg.payload == b'move back':
            mymovehub.run_motor_for_time(MOTOR_AB, UNIT_MOVE_MSEC, -UNIT_MOVE_POWER)
        elif msg.payload == b'move around':
            mymovehub.run_motors_for_time(MOTOR_AB, UNIT_MOVE_MSEC*2, UNIT_MOVE_POWER, -UNIT_MOVE_POWER)
        elif msg.payload == b'move random':
            for i in range(100):
                print(i, randint(-50, 50))
                mymovehub.run_motors_for_time(MOTOR_AB, UNIT_MOVE_MSEC, randint(-50*2, 50*2), randint(-50*2,50*2))
                time.sleep(0.1)
        else:
            print("Direction unknown!")
    except Exception as e:
        print(e, e.inspect)
    finally:
        pass

MQTT_SERVER = "localhost"
MQTT_PATH_SS = "lifidea/boost/request"

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883, 60)
client.loop_start()

while(1):
    try:
        time.sleep(1)
        print('Color: {} Distance: {}'.format(mymovehub.last_color_D, mymovehub.last_distance_D))
        if mymovehub.last_distance_D < 10:
            mymovehub.run_motor_for_time(MOTOR_AB, UNIT_MOVE_MSEC * (10 - mymovehub.last_distance_D) / 2, -UNIT_MOVE_POWER)
    except Exception as e:
        print(e)
        pdb.set_trace()
