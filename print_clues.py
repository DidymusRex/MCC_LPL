#!/usr/bin/env python
# ------------------------------------------------------------------------------
# file: print_clues.py
# desc: print out all the clues to check formatting for the LPL game
# Dec 2024: Original code
# ------------------------------------------------------------------------------
from game_data import *
from config import *
from escpos import *
import paho.mqtt.client as mqtt

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

def print_message(k,v):
    p.text(f"{k}\n\n")
    p.text(f"{v}\n\n")
    p.text("----.----0----.----0----.---0----.---0----\n")

p.set(align='LEFT', font='B', width=1, height=1)
p.text('Font B max chars 44\n')
p.text("----.----0----.----0----.---0----.---0----\n")

for k, v in ErrorMessages.items():
    print_message(k,v)

for k, v in passkey_clues.items():
    print_message(k,v)

for k, v in artifact_clues.items():
    print_message(k,v)

p.cut()
