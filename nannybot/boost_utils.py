import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

MQTT_SERVER = "localhost"
MQTT_PATH_SS = "lifidea/boost/request"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_PATH_SS)

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def send_cmd(dir, time=1):
    print("[send_cmd] {} {}".format(dir, time))
    publish.single(MQTT_PATH_SS, json.dumps({"dir":dir, "time":time}) , hostname=MQTT_SERVER)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883, 60)
