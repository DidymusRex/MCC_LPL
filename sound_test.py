#!/usr/bin/env python
from config import *
import os
from pygame import mixer
from subprocess import call
import time

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

# pygam mixer setup
mixer.init()
play_sound('334261__projectsu012__coin-chime.wav')
speak_text('check check 1 2 3')
