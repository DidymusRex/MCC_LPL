import paho.mqtt.client as mqtt
import sys
from time import sleep
"""
A simple, generic MQTT client to send MQTT commands for testing
"""

"""
MQTT values
"""
mqtt_broker = "mcc-lpl.local"
mqtt_account = "mcc"
mqtt_passwd = "mcc"

topic = sys.argv[1]
payload = sys.argv[2]

def on_connect(client, userdata, flags, rc):
    print("Connected with result code {}".format(rc))

def on_publish(client, userdata, mid):
    print("published message id {}".format(mid))
 
mqc = mqtt.Client()
mqc.on_connect = on_connect
mqc.on_publish = on_publish

mqc.username_pw_set(mqtt_account, mqtt_passwd)
mqc.connect(mqtt_broker)

mqc.loop_start()
print("publishing topic {} payload {}".format(topic, payload))
rc = mqc.publish(topic, payload, 0)

sleep(5)
print("rc = {} mid = {} is_published = {}".format(rc.rc, rc.mid, rc.is_published()))
mqc.loop_stop()
