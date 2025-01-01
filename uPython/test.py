# ------------------------------------------------------------------------------
# file: test.py
# desc: basic card reader test for the LPL game
# Dec 2024: Original code
# ------------------------------------------------------------------------------
from machine import Pin, SPI
from mfrc522 import MFRC522
import time

rfid = MFRC522(cs=17,
               sck=18,
               mosi=19,
               miso=16,
               rst=22,
               # irq=2,
               # callback=card_detected_callback,
               baudrate=100000,
               spi_id=0)

rfid.init()
(stat, tag_type) = rfid.request(rfid.REQIDL)
print(f'stat ..... {stat}')
print(f'tag_type . {tag_type}')

(status, uid) = rfid.anticoll(rfid.PICC_ANTICOLL1)
print(f'status ... {status}')
print(f'uid ...... {uid}')

'''
byte5 = 0
for i in uid:
    print(f'before: {byte5}')
    byte5 = byte5 ^ i
    print(f'after : {byte5}')
puid = uid + [byte5]
print(f'uid: {uid} puid{puid}')
'''
