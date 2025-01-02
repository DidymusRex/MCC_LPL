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
from players import *
from pygame import mixer
from subprocess import call
import time
import uuid

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def welcome_player(m):
        pass

# ------------------------------------------------------------------------------
def process_player(m):
        active_player = m

        if player_status[m] == 'inactive':
                player_status[m] = 'checked-in'
                welcome_player(m)
                print_clue(m)
        else:
                player_status[m] = 'active'

# ------------------------------------------------------------------------------
def process_passkey(m):
        if active_player is None:
                speak_text(ErrorMessage['NotAuthenticated'])
                return

        if m != player_assigment[active_player]:
                # this leaks a little information about the passkey
                if m in active_passkeys:
                        speak_text(ErrorMessage['WrongPasskey'])
                else:
                        speak_text(ErrorMessage['NotLost'])
        else:
                player_status[active_player] = 'searching'
                print_search(m)

# ------------------------------------------------------------------------------
def print_search(m):
        pass

# ------------------------------------------------------------------------------
def test_printer(p):
        p.set(align='LEFT', font='A', width=1, height=1)
        p.text('Font A max chars 33\n')
        p.text("----.----0----.----0----.---0---\n")
        p.text(time.strftime('%a %b %d %Y %r\n'))

        p.set(align='LEFT', font='B', width=1, height=1)
        p.text('Font B max chars 44\n')
        p.text("----.----0----.----0----.---0----.---0----\n")
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
def library_header():
        # Library Logo
        p.set(align='CENTER', font='A', width=1, height=1)
        p.image('images/MCCL_LogoC.png')
        p.text('Miscatonic Community College\n')

        p.set(width=2, height=2)
        p.text('Library\n')

# ------------------------------------------------------------------------------
def print_clue(m):
        library_header()
        p.set(align='LEFT', font='B', width=1, height=1)
        p.text(clues_choose[player_assignment[m]])

        p.cut()
# ------------------------------------------------------------------------------
def print_book_info(title, author, isbn):
        p.set(align='LEFT', font='B', width=1, height=1)
        p.text('\nTitle:')
        p.text(title)        
        p.text('\nAuthor:')
        p.text(author)
        p.text('\nISBN:')
        p.text(isbn)
        p.text('\n\n')
        p.barcode(isbn, 'EAN13', 64, 3, 'OFF', 'A' )
        p.set(align='LEFT', font='A', width=1, height=1)
        p.text('Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.')

# ------------------------------------------------------------------------------
def play_sound(sound_file):
        print(f'play sound: {sound_file}')

        mixer.music.load(sfx_location + sound_file)
        mixer.music.play()

# ------------------------------------------------------------------------------
def speak_text(text):
        print("speaking text")
        with open("temp.txt", "w") as temp:
        temp.write(text)

        cmd="cat temp.txt|espeak -ven+m4 -g5 -s160"
        call([cmd],shell=True)

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

        if   topic == 'mcc/player':
                process_player(message)
        elif topic == 'mcc/passkey'
                process_passkey(message)
        elif topic == 'mcc/active_passkey'
                process_active_passkey(message)
        else:
                print(f"--- ignoring {topic} {message} ---")
 
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
def main():
        mixer.init()
        p.hw('INIT')

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

        while True:
                time.sleep(.1)

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
if __name__ == "__main__":
        # Configure Printer
        printer_type="Usb"
        printer_vendor=0x28e9
        printer_product=0x0289
        printer_interface=0
        printer_in_ep=0x81
        printer_out_ep=0x03
        printer_profile="simple"

        p = printer.Usb(printer_vendor,
                printer_product,
                printer_interface,
                printer_in_ep,
                printer_out_ep)

        active_player = None

        print("BEGIN")
        main()
