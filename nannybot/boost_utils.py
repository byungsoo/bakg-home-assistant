import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

MQTT_SERVER = "localhost"
MQTT_PATH_SS = "lifidea/boost/request"

UNIT_MOVE_MSEC = 100
UNIT_MOVE_POWER = 100

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_PATH_SS)

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883, 60)

def send_cmd(dir, time=1):
    publish.single(MQTT_PATH_SS, json.dumps({"dir":dir, "time":time}) , hostname=MQTT_SERVER)

def move_smooth(motor, time, dir=1, discount=2):
    mymovehub.run_motor_for_time(motor, int(time*UNIT_MOVE_MSEC), UNIT_MOVE_POWER*dir)
    mymovehub.run_motor_for_time(motor, int(time*UNIT_MOVE_MSEC/discount), UNIT_MOVE_POWER/discount*dir)
