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
def process_player(player):
        """
        An ID card has ben scanned
        """
        global active_player

        print(f'process_player({player})')

        if player not in player_status:
                speak_text('Invalid ID detected, the authorities have been notified')
                return

        if player == active_player:
                 speak_text(f'{player}, you are already authenticated.')
                 return

        active_player = player

        if player_status[player] == 'inactive':
                speak_text(f'welcome, {player}. You have been authenticated')
                print_passkey_clue(player)
                player_status[player] = 'active'

        elif player_status[player] == 'active':
                speak_text(f'{player}, please scan a passkey')

        elif player_status[player] == 'passkey':
                speak_text(f'{player}, please scan an artifact')

        else:
                player_status[player] = 'active'

# ------------------------------------------------------------------------------
def process_passkey(passkey):
        print(f'process_passkey({passkey})')
        global active_player

        if active_player == 'None':
                speak_text(ErrorMessages['NotAuthenticated'])
                return

        if passkey == player_assignment[active_player]:
                print_artifact_clue(passkey)
                player_status[active_player] = 'passkey'

        else:
                speak_text(ErrorMessages['WrongPasskey'])

# ------------------------------------------------------------------------------
def process_artifact(artifact):
        print(f'process_artifact({artifact})')
        global active_player

        if active_player == 'None':
                speak_text(ErrorMessages['NotAuthenticated'])
                return

        if artifact == player_assignment[active_player]:
                artifacts[artifact] = 'found'
                player_status[active_player] = 'artifact'

                # have all artifacts been checked in?
                if 'lost' in artifacts.values():
                        # we keep looking for more artifacts
                        print_final_clue(artifact)
                else:
                        print_final_clue('final')
        else:
                speak_text(ErrorMessages['WrongArtifact'])

# ------------------------------------------------------------------------------
def print_library_header():
        # Library Logo
        p.set(align='CENTER', font='A', width=1, height=1)
        p.image('images/MCCL_Logo_C.png')
        p.text('Miscatonic Community College\n')

        p.set(align='CENTER', font='A', width=2, height=2)
        p.text('Library\n')

# ------------------------------------------------------------------------------
def print_passkey_clue(passkey):
        print(f'print_passkey_clue({passkey}) for {player_assignment[active_player]}')

        print_library_header()
        p.set(align='LEFT', font='A', width=2, height=2)
        p.text(active_player)
        p.set(align='LEFT', font='B', width=1, height=1)
        p.text(passkey_clues[player_assignment[active_player]])

        p.cut()

# ------------------------------------------------------------------------------
def print_artifact_clue(artifact):
        print(f'print_artifact_clue({artifact}) for {player_assignment[active_player]}')

        print_library_header()
        p.set(align='LEFT', font='A', width=2, height=2)
        p.text(active_player)
        p.set(align='LEFT', font='B', width=1, height=1)
        p.text(artifact_clues[player_assignment[active_player]])

        p.cut()

# ------------------------------------------------------------------------------
def print_final_clue(artifact):
        pass

# ------------------------------------------------------------------------------
def play_sound(sound_file):
        print(f'play_sound({sound_file})')

        sfx = mixer.Sound(sfx_location + sound_file)
        sfx.play()

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
        # Start the MQTT loop
        print('MQTT client loop')
        mqtt_client.loop_start()

        while True:
                time.sleep(.1)

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
active_player = 'None'
active_passkey = 'None'
active_artifact = 'None'

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

play_sound('34141__erh__swell-pad.wav')
speak_text('the library is now open for business')
active_player = 'none'

print('BEGIN')

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

if __name__ == '__main__':
        main()
