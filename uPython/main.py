# ------------------------------------------------------------------------------
# file: main.py
# desc: the RFID scan and publish logic in uPython for the LPL game
# Dec 2024: Original code
# ------------------------------------------------------------------------------
from config import *
from game_data import *
import machine
from mfrc522 import MFRC522
import network
import time
import random
import ubinascii
from umqtt.simple import MQTTClient

# ------------------------------------------------------------------------------
# Define a callback function to handle incoming MQTT messages
def subscription_callback():
    print(f'sub- topic .: {topic.decode()}')
    print(f'sub- message: {msg.decode()}')

# ------------------------------------------------------------------------------
# failsafe for MQTT failure - turn it off and on again
def reset():
    print('Resetting...')
    time.sleep(5)
    machine.reset()

# ------------------------------------------------------------------------------
# Define a callback function to handle scanned cards
def card_detected_callback(uid):
    print(f"Card UID: {uid}")

# ------------------------------------------------------------------------------
def read_data_block(reader, uid, sector, block, keyA):
    block_address = sector * 4 + block

    # Authenticate for the block
    status = reader.authKeys(uid, block_address, keyA)
    if status != reader.OK:
        print(f"Authentication failed for block {block_address}")
        return

    # Read the block
    status, data = reader.read(block_address)
    reader.stop_crypto1()  # Stop encryption after reading

    if status == reader.OK:
        print(f"Block {block_address} contents: {data}")
        return data
    else:
        print(f"Failed to read block {block_address}")
        return None

# ------------------------------------------------------------------------------
def read_card(reader, uid):
    card_data = list()

    for sector in range(16):
        keyA = rfid.read_sector_keyA(uid, sector)

        for block in range(4):
            data = read_data_block(reader, uid, sector, block, keyA)
            card_data.append(data)

    return card_data

# ------------------------------------------------------------------------------
def write_blocks(reader, uid):
# Function to write all blocks with 1s (0xFF)
    data = [0xFF] * 16  # Data filled with 1s
    keyA = [0xFF] * 6   # Default key for authentication

    for sector in range(16):  # Loop through all sectors
        for block in range(3):  # Loop through blocks (0–2 are writable in each sector)
            if block == 3:
                print('skip block trailer')
                continue

            block_address = (sector * 4) + block

            # Authenticate for the block
            status = reader.authKeys(uid, block_address, keyA)
            if status != reader.OK:
                print(f"Authentication failed for Sector {sector}, Block {block}")
                continue

            # Write data to the block
            status = reader.write(block_address, data)
            if status == reader.OK:
                print(f"Written to Sector {sector}, Block {block}, data{data}")
            else:
                print(f"Failed to write to Sector {sector}, Block {block}")

    reader.stop_crypto1()
    print("All writable blocks updated with 1s.")

# ------------------------------------------------------------------------------
def read_uid():
    rfid.init()
    (stat, tag_type) = rfid.request(rfid.REQIDL)

    status = None
    uid = None

    if stat == rfid.OK:
        # Perform anticollision to get UID
        (status, uid) = rfid.anticoll(rfid.PICC_ANTICOLL1)

    return uid

# ------------------------------------------------------------------------------
def process_tag(uid):
    k = str(uid)

    # check for a player
    if k in players:
        topic='mcc/player'
        message=players[k]
    # check for artifact
    elif k in artifacts:
        topic='mcc/artifact'
        message=artifacts[k]
    # unknown tag
    else:
        topic='mcc'
        message='Error'

    print(f'\nuid is {k} : {message}')
    mqttClient.publish(topic, message.encode())

# ------------------------------------------------------------------------------
def main():
    print("Searching for tags")
    count = 0
    while True:
        count = count + 1
        if count > 49:
            print('.')
            count = 0
        else:
            print('*', end='')

        uid = []
        uid = read_uid()
        if uid:
            process_tag(uid)

            # don't read another RFID for at least 5 seconds
            time.sleep(5)
        else:
            time.sleep(.1)

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    # Initialize the MFRC522 module
    rfid = MFRC522(cs=17,
                sck=18,
                mosi=19,
                miso=16,
                rst=22,
                # irq=20,
                # callback=card_detected_callback,
                baudrate=100000,
                spi_id=0)

    print(f"connecting to {SSID}")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(SSID, SSID_PW)

    while not sta_if.isconnected(): time.sleep(.1)

    print(f'Define  MQTTClient       :: {MQTT_ID} on {MQTT_BROKER} as {MQTT_USER}')
    mqttClient = MQTTClient(MQTT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PW, keepalive=60)
    print(f'Set callback             :: sub-cb')
    mqttClient.set_callback(subscription_callback)
    print(f'Connect to MQTT Broker   :: {MQTT_BROKER}')
    mqttClient.connect()
    print(f'subscribing to           :: {MQTT_SUB}')
    mqttClient.subscribe(MQTT_SUB)

    print(f'Connected to MQTT Broker :: {MQTT_BROKER}')
    print(f'Subscribed to            :: {MQTT_SUB}')

    # failsafe for MQTT connection errors. Turn it off and turn it on again
    print('trying main()')
    try:
        main()
    except OSError as e:
        print(f"Error {e} resetting.")
        reset()

# ------------------------------------------------------------------------------


