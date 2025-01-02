#!/usr/bin/env python
# ------------------------------------------------------------------------------
# file: read_RFID.py
# desc: the RFID scan and publish logic in uPython for the LPL game
# Jan 2025: Original code adapted from MCRF522-python
# ------------------------------------------------------------------------------
from config import *
from game_data import *
import os
import paho.mqtt.client as mqtt
from pygame import mixer
from subprocess import call
import time
import uuid
import RPi.GPIO as GPIO
import mfrc522
import signal


# ------------------------------------------------------------------------------
# Capture SIGINT for cleanup when the script is terminated
def end_read(signal,frame):
    global continue_reading
    print ("\nCtrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

# ------------------------------------------------------------------------------
def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribe to the MQTT topics upon successful connection
        client.subscribe("mcc/#")

# ------------------------------------------------------------------------------
def on_message(client, userdata, msg):
        topic = msg.topic
        message = msg.payload.decode("utf-8")

        print(f'sub- topic: {topic}')
        print(f'sub- message: {message}')
 
# ------------------------------------------------------------------------------
def publish_message(topic, message):
        # Publish the message
        print(f'pub- topic: {topic}')
        print(f'pub- message: {message}')

        mqtt_client.publish(topic, message)

# ------------------------------------------------------------------------------
def publish_reset(topic):
        # Publish the message "reset" to the specified MQTT topic
        print(f'Sending reset to {topic}')

        mqtt_client.publish(topic, "reset")

# ------------------------------------------------------------------------------
def process_tag(uid):
    k = str(uid)

    # check for a player
    if k in players:
        topic='mcc/player'
        message=players[k]
    # check for passkey
    elif k in passkeys:
        topic='mcc/passkey'
        message=passkeys[k]
    # unknown tag
    else:
        topic='mcc'
        message='Unknown RFID item'

    print(f'\nuid is {k} : {message}')
    publish_message(topic, message.encode())

# ------------------------------------------------------------------------------
# This loop keeps checking for chips. If one is near it will get the UID and authenticate
def main():
    while continue_reading:
        
        # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:
            print ("Card detected")
        
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:

            # Print UID
            print ("Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))

            # process the tag. Add a short delay to avoid 2x reads
            process_tag(uid)
            time.sleep(2)
        
            """
            We don't need to authenticate, we only care about the uid.
            This code left in place for reference later.

            # This is the default key for authentication
            key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
            
            # Select the scanned tag
            MIFAREReader.MFRC522_SelectTag(uid)

            # Authenticate
            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

            # Check if authenticated
            if status == MIFAREReader.MI_OK:
                MIFAREReader.MFRC522_Read(8)
                MIFAREReader.MFRC522_StopCrypto1()

                # process the tag. Add a short delay to avoid 2x reads
                process_tag(uid)
                time.sleep(2)
            else:
                print ("Authentication error")
            """

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Hook the SIGINT
    signal.signal(signal.SIGINT, end_read)

    # Create an object of the class mfrc522
    MIFAREReader = mfrc522.MFRC522()

    # MQTT client setup
    print('MQTT client setup')
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(username=mqtt_username, password=mqtt_password)
    mqtt_client.on_message = on_message
    mqtt_client.on_connect = on_connect

    # Connect to the MQTT broker
    print('MQTT client connect')
    mqtt_client.connect(mqtt_broker, mqtt_port, 60)

    # Start the MQTT loop
    print('MQTT client loop')
    mqtt_client.loop_start()
    
    continue_reading = True

    main()
