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
from subprocess import call8
import time
import uuid

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def process_player(player):
        print(f'process_player({player})')

        global active_player

        active_player = player

        if player_status[player] == 'inactive':
                player_status[player] = 'passkey'
                speak_text(f'welcome, {player}.')
                print_passkey_clue(player)

        elif player_status[player] == 'passkey':
                player_status[player] = 'artifact'
                speak_text(f'{player}, please scan your passkey')

        elif player_status[player] == 'artifact':
                player_status[player] = 'final'

        else:
                player_status[player] = 'active'

# ------------------------------------------------------------------------------
def process_passkey(passkey):
        print(f'process_passkey({passkey})')
        global active_player

        if active_player == 'none':
                speak_text(ErrorMessages['NotAuthenticated'])
                return

        if passkey != player_assignment[active_player]:
                # this leaks a little information about the passkey
                if passkey in artifacts:
                        speak_text(ErrorMessages['WrongPasskey'])
                else:
                        speak_text(ErrorMessages['NotLost'])
        else:
                player_status[active_player] = 'passkey'
                print_artifact_clue(passkey)

# ------------------------------------------------------------------------------
def process_artifact(artifact):
        print(f'process_artifact({artifact})')
        global active_player

        if active_player == 'none':
                speak_text(ErrorMessages['NotAuthenticated'])
                return

        if artifact != player_assignment[active_player]:
                # this leaks a little information about the passkey
                if artifact in artifacts:
                        speak_text(ErrorMessages['WrongPasskey'])
                else:
                        speak_text(ErrorMessages['NotLost'])
        else:
                player_status[active_player] = 'artifact'
                artifacts[artifact] = 'found'
                # have all artifacts been checked in?
                if 'lost' in artifacts.values():
                        # we keep lookin for more artifacts
                        print_final_clue(artifact)
                else:
                        print_final_clue('final')

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
        p.text(time.strftime('%a %b %d %Y %r\n\n'))

        p.set(align='CENTER')
        v = '2695880042000'
        p.barcode(v, 'EAN13', 64, 2, 'OFF', 'B')
        p.text(v)

        p.image('images/MCCL_Logo_C.png')

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

        p.set(align='CENTER', font='A', width=2, height=2)
        p.text('Library\n')

# ------------------------------------------------------------------------------
def print_passkey_clue(passkey):
        print(f'print_passkey_clue({passkey}) for {player_assignment[passkey]}')

        global p
        print_library_header()
        p.set(align='LEFT', font='B', width=1, height=1)
        p.text(passkey_clues[player_assignment[passkey]])

        p.cut()

# ------------------------------------------------------------------------------
def print_artifact_clue(artifact):
        print(f'print_artifact_clue({artifact}) for {player_assignment[artifact]}')
        global p
        print_library_header()
        p.set(align='LEFT', font='B', width=1, height=1)
        p.text(artifact_clues[player_assignment[artifact]])

        p.cut()

# ------------------------------------------------------------------------------
def print_final_clue(artifact):
        pass

# ------------------------------------------------------------------------------
def play_sound(sound_file):
        print(f'play_sound({sound_file})')

        mixer.music.load(sfx_location + sound_file)
        mixer.music.play()

# ------------------------------------------------------------------------------
def speak_text(text):
        print('speaking text')
        with open('temp.txt', 'w') as temp:
                temp.write(text)

        time.sleep(.5)
        cmd='cat temp.txt|espeak -ven+f3 -g5 -s160'
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

        # We may begin!
        print_library_header()
        p.cut()
        
        speak_text('the library is now open for business')
        active_player = 'none'

        print('BEGIN')
        main()
