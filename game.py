#!/usr/bin/env python
# ------------------------------------------------------------------------------
# file: game.py
# desc: the audio and printing logic for the LPL game
# Dec 2024: Original code
# ------------------------------------------------------------------------------

from config import *
from escpos import *
from game_data import *
import paho.mqtt.client as mqtt
import os
from pygame import mixer
from subprocess import call
import time
import uuid

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def welcome_player(m):
        speak_text(f'welcome, {m}.')

# ------------------------------------------------------------------------------
def process_player(m):
        active_player = m

        if player_status[m] == 'inactive':
                player_status[m] = 'passkey'
                welcome_player(m)
                print_passkey_clue(m)

        elif player_status[m] == 'passkey':
                player_status[m] = 'artifact'
                speak_text(f'{m}, please scan your passkey')

        elif player_status[m] == 'artifact':
                player_status[m] = 'final'

        else:
                player_status[m] = 'active'

# ------------------------------------------------------------------------------
def process_passkey(m):
        if active_player == None:
                speak_text(ErrorMessages['NotAuthenticated'])
                return

        if m != player_assignment[active_player]:
                # this leaks a little information about the passkey
                if m in active_passkeys:
                        speak_text(ErrorMessages['WrongPasskey'])
                else:
                        speak_text(ErrorMessages['NotLost'])
        else:
                player_status[active_player] = 'passkey'
                print_passkey_clue(m)

# ------------------------------------------------------------------------------
def process_artifact(m):
        pass

# ------------------------------------------------------------------------------
def test_printer():
        global p

        p.set(align='LEFT', font='A', width=1, height=1)
        p.text('Font A max chars 33\n')
        p.text('----.----0----.----0----.---0---\n')
        p.text(time.strftime('%a %b %d %Y %r\n'))

        p.set(align='LEFT', font='B', width=1, height=1)
        p.text('Font B max chars 44\n')
        p.text('----.----0----.----0----.---0----.---0----\n')
        p.text(time.strftime('%a %b %d %Y %r\n'))

        p.set(align='CENTER')
        v = '2695880042000'
        p.barcode(v, 'EAN13', 64, 2, 'OFF', 'B')
        p.text(v)

        v=str(uuid.uuid4())
        p.qr(v, size=6)
        p.text(v)
        # Feed some paper
        p.cut()

# ------------------------------------------------------------------------------
def print_library_header():
        global p
        # Library Logo
        p.set(align='CENTER', font='A', width=1, height=1)
        p.image('images/MCCL_Logo_C.png')
        p.text('Miscatonic Community College\n')

        p.set(width=2, height=2)
        p.text('Library\n')

# ------------------------------------------------------------------------------
def print_passkey_clue(m):
        global p
        print_library_header()
        p.set(align='LEFT', font='B', width=1, height=1)
        p.text(passkey_clues[player_assignment[m]])

        p.cut()

# ------------------------------------------------------------------------------
def print_artifact_clue(m):
        global p
        print_library_header()
        p.set(align='LEFT', font='B', width=1, height=1)
        p.text(artifact_clues[player_assignment[m]])

        p.cut()

# ------------------------------------------------------------------------------
def play_sound(sound_file):
        print(f'play sound: {sound_file}')

        mixer.music.load(sfx_location + sound_file)
        mixer.music.play()

# ------------------------------------------------------------------------------
def speak_text(text):
        print('speaking text')
        with open('temp.txt', 'w') as temp:
                temp.write(text)

        cmd='cat temp.txt|espeak -ven+m4 -g5 -s160'
        call([cmd],shell=True)

# ------------------------------------------------------------------------------
def on_connect(client, userdata, flags, rc):
        print('Connected with result code ' + str(rc))

        # Subscribe to the MQTT topics upon successful connection
        client.subscribe('mcc/#')

# ------------------------------------------------------------------------------
def on_message(client, userdata, msg):
        topic = msg.topic
        message = msg.payload.decode('utf-8')

        print(f'sub- topic: {topic}')
        print(f'sub- message: {message}')

        if   topic == 'mcc/player':
                process_player(message)
        elif topic == 'mcc/passkey':
                process_passkey(message)
        elif topic == 'mcc/artifact':
                process_artifact(message)
        else:
                print(f'--- ignoring {topic} {message} ---')
 
# ------------------------------------------------------------------------------
def publish_message(topic, message):
        # Publish the message
        print(f'pub- topic: {topic}')
        print(f'pub- message: {message}')

        mqtt_client.publish(topic, message)

# ------------------------------------------------------------------------------
def publish_reset(topic):
        # Publish the message 'reset' to the specified MQTT topic
        print(f'Sending reset to {topic}')

        mqtt_client.publish(topic, 'reset')

# ------------------------------------------------------------------------------
def main():
        global p, mqtt_client

        # Start the MQTT loop
        print('MQTT client loop')
        mqtt_client.loop_start()

        while True:
                time.sleep(.1)

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
if __name__ == '__main__':
        # Configure Printer
        printer_type='Usb'
        printer_vendor=0x28e9
        printer_product=0x0289
        printer_interface=0
        printer_in_ep=0x81
        printer_out_ep=0x03
        printer_profile='simple'

        p = printer.Usb(printer_vendor,
                printer_product,
                printer_interface,
                printer_in_ep,
                printer_out_ep)
        p.hw('INIT')

        # MQTT client setup
        print('MQTT client setup')
        mqtt_client = mqtt.Client()
        mqtt_client.username_pw_set(username=mqtt_username, password=mqtt_password)
        mqtt_client.on_message = on_message
        mqtt_client.on_connect = on_connect

        # pygam mixer setup
        mixer.init()

        # Connect to the MQTT broker
        print('MQTT client connect')
        mqtt_client.connect(mqtt_broker, mqtt_port, 60)
        test_printer()
        speak_text('the library is now open for business')
        active_player = None

        print('BEGIN')
        main()
