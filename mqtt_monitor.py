#!/usr/bin/env python

import paho.mqtt.client as mqtt
"""
A simple, generic MQTT client to monitor MQTT commands and
results
"""

"""
MQTT values
"""
mqtt_broker = "mcc-league.local"
mqtt_account = "mcc"
mqtt_passwd = "mcc"
mqtt_topic = "mcc/#"

"""
MQTT connect callback
    Subscribing in on_connect() means that if we lose the connection and
    reconnect then subscriptions will be renewed.
"""
def on_connect(client, userdata, flags, rc):
    client.subscribe(mqtt_topic)

"""
MQTT receive message callback
"""
def on_message(client, userdata, msg):
    print("message topic .......:",msg.topic)
    print("message message .....:",msg.payload.decode('utf-8'))
    # print("message qos .........:",msg.qos)
    # print("message retain flag .:",msg.retain)
    print("-" * 40)

mqc = mqtt.Client(client_id="monitor",
                  clean_session=True,
                  userdata=None,
                  protocol=mqtt.MQTTv311,
                  transport="tcp")
mqc.on_connect = on_connect
mqc.on_message = on_message

mqc.username_pw_set(mqtt_account, mqtt_passwd)
mqc.connect(mqtt_broker)

print(f"connected to {mqtt_broker} monitoring topic {mqtt_topic}")
mqc.loop_forever()
