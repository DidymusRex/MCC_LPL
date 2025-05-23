from machine import Pin, SPI
from os import uname
import sys
"""
https://how2electronics.com/using-rc522-rfid-reader-module-with-raspberry-pi-pico/
"""
 
class MFRC522:
 
    DEBUG = True
    OK = 0
    NOTAGERR = 1
    ERR = 2

    # MFRC522 Command Codes
    COMMAND_IDLE = 0x00          # No action, cancel current command
    COMMAND_MEM = 0x01           # Store 25 bytes into the internal buffer
    COMMAND_GENERATE_RANDOM_ID = 0x02  # Generate a 10-byte random ID
    COMMAND_CALC_CRC = 0x03      # Activate CRC coprocessor
    COMMAND_TRANSMIT = 0x04      # Transmit data from FIFO buffer
    COMMAND_NO_CMD_CHANGE = 0x07 # Maintain current command
    COMMAND_RECEIVE = 0x08       # Activate receiver circuits
    COMMAND_TRANSCEIVE = 0x0C    # Transmit data and receive response
    COMMAND_MFAUTHENT = 0x0E     # Perform MIFARE authentication
    COMMAND_SOFT_RESET = 0x0F    # Reset the MFRC522 chip

    # MIFARE Commands
    MIFARE_AUTHENT1A = 0x60      # Authenticate using Key A
    MIFARE_AUTHENT1B = 0x61      # Authenticate using Key B
    MIFARE_READ = 0x30           # Read a block (16 bytes)
    MIFARE_WRITE = 0xA0          # Write a block (16 bytes)
    MIFARE_INCREMENT = 0xC1      # Increment a block's value
    MIFARE_DECREMENT = 0xC0      # Decrement a block's value
    MIFARE_RESTORE = 0xC2        # Restore block to transfer buffer
    MIFARE_TRANSFER = 0xB0       # Transfer buffer to block
    MIFARE_DEFAULT_KEY = [0xff] * 6	# Default key value

    # Request Modes
    REQIDL = 0x26                # Request cards in idle state
    REQALL = 0x52                # Request all cards in range

    # Default Block Sizes
    BLOCK_SIZE = 16              # Block size in bytes (16 bytes per block)

    # Other Constants
    MAX_UID_LENGTH = 10          # Maximum UID length for anticollision
    FIFO_BUFFER_SIZE = 64        # FIFO buffer size of the MFRC522

    PICC_ANTICOLL1 = 0x93
    PICC_ANTICOLL2 = 0x95
    PICC_ANTICOLL3 = 0x97

# ------------------------------------------------------------------------------
    def __init__(self, sck, mosi, miso, rst, cs, baudrate=1000000,spi_id=0):
        self.sck = Pin(sck, Pin.OUT)
        self.mosi = Pin(mosi, Pin.OUT)
        self.miso = Pin(miso)
        self.rst = Pin(rst, Pin.OUT)
        self.cs = Pin(cs, Pin.OUT)
 
        self.rst.value(0)
        self.cs.value(1)
        
        board = uname()[0]
 
        if board == 'WiPy' or board == 'LoPy' or board == 'FiPy':
            self.spi = SPI(0)
            self.spi.init(SPI.MASTER, baudrate=1000000, pins=(self.sck, self.mosi, self.miso))

        elif (board == 'esp8266') or (board == 'esp32'):
            self.spi = SPI(baudrate=100000, polarity=0, phase=0, sck=self.sck, mosi=self.mosi, miso=self.miso)
            self.spi.init()

        elif board == 'rp2':
            self.spi = SPI(spi_id,baudrate=baudrate,sck=self.sck, mosi= self.mosi, miso= self.miso)

        else:
            raise RuntimeError("Unsupported platform")
 
        self.rst.value(1)
        self.init()
 
# ------------------------------------------------------------------------------
    def _wreg(self, reg, val):
        self.cs.value(0)
        self.spi.write(b'%c' % int(0xff & ((reg << 1) & 0x7e)))
        self.spi.write(b'%c' % int(0xff & val))
        self.cs.value(1)
 
# ------------------------------------------------------------------------------
    def _rreg(self, reg):
        self.cs.value(0)
        self.spi.write(b'%c' % int(0xff & (((reg << 1) & 0x7e) | 0x80)))
        val = self.spi.read(1)
        self.cs.value(1)
 
        return val[0]
 
# ------------------------------------------------------------------------------
    def _sflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) | mask)
 
# ------------------------------------------------------------------------------
    def _cflags(self, reg, mask):
        self._wreg(reg, self._rreg(reg) & (~mask))
 
# ------------------------------------------------------------------------------
    def _tocard(self, cmd, send):
        recv = []
        bits = irq_en = wait_irq = n = 0
        stat = self.ERR
 
        if cmd == 0x0E:
            irq_en = 0x12
            wait_irq = 0x10

        elif cmd == 0x0C:
            irq_en = 0x77
            wait_irq = 0x30
 
        self._wreg(0x02, irq_en | 0x80)
        self._cflags(0x04, 0x80)
        self._sflags(0x0A, 0x80)
        self._wreg(0x01, 0x00)
 
        for c in send:
            self._wreg(0x09, c)

        self._wreg(0x01, cmd)
 
        if cmd == 0x0C:
            self._sflags(0x0D, 0x80)
 
        i = 2000
        while True:
            n = self._rreg(0x04)
            i -= 1
            if ~((i != 0) and ~(n & 0x01) and ~(n & wait_irq)):
                break
 
        self._cflags(0x0D, 0x80)
 
        if i:
            if (self._rreg(0x06) & 0x1B) == 0x00:
                stat = self.OK
 
                if n & irq_en & 0x01:
                    stat = self.NOTAGERR

                elif cmd == 0x0C:
                    n = self._rreg(0x0A)
                    lbits = self._rreg(0x0C) & 0x07

                    if lbits != 0:
                        bits = (n - 1) * 8 + lbits
                    else:
                        bits = n * 8
 
                    if n == 0:
                        n = 1
                    elif n > 16:
                        n = 16
 
                    for _ in range(n):
                        recv.append(self._rreg(0x09))
            else:
                stat = self.ERR
 
        return stat, recv, bits
 
# ------------------------------------------------------------------------------
    def _crc(self, data):
        self._cflags(0x05, 0x04)
        self._sflags(0x0A, 0x80)
 
        for c in data:
            self._wreg(0x09, c)
 
        self._wreg(0x01, 0x03)
 
        i = 0xFF
        while True:
            n = self._rreg(0x05)
            i -= 1

            if not ((i != 0) and not (n & 0x04)):
                break
 
        return [self._rreg(0x22), self._rreg(0x21)]
 
# ------------------------------------------------------------------------------
    def init(self):
        self.reset()
        self._wreg(0x2A, 0x8D)
        self._wreg(0x2B, 0x3E)
        self._wreg(0x2D, 30)
        self._wreg(0x2C, 0)
        self._wreg(0x15, 0x40)
        self._wreg(0x11, 0x3D)
        self.antenna_on()
 
# ------------------------------------------------------------------------------
    def reset(self):
        self._wreg(0x01, 0x0F)
 
# ------------------------------------------------------------------------------
    def antenna_on(self, on=True):
        if on and ~(self._rreg(0x14) & 0x03):
            self._sflags(0x14, 0x03)
        else:
            self._cflags(0x14, 0x03)
 
# ------------------------------------------------------------------------------
    def request(self, mode): 
        self._wreg(0x0D, 0x07)
        (stat, recv, bits) = self._tocard(0x0C, [mode])
 
        if (stat != self.OK) | (bits != 0x10):
            stat = self.ERR
 
        return stat, bits
  
# ------------------------------------------------------------------------------
    def anticoll(self,anticolN): 
        ser_chk = 0
        ser = [anticolN, 0x20]
 
        self._wreg(0x0D, 0x00)
        (stat, recv, bits) = self._tocard(0x0C, ser)
 
        if stat == self.OK:
            if len(recv) == 5:
                for i in range(4):
                    ser_chk = ser_chk ^ recv[i]
                if ser_chk != recv[4]:
                    stat = self.ERR
            else:
                stat = self.ERR
 
        return stat, recv

# ------------------------------------------------------------------------------
    def PcdSelect(self, serNum, anticolN):
        backData = []
        buf = []
        buf.append(anticolN)
        buf.append(0x70)

        for i in serNum:
            buf.append(i)

        pOut = self._crc(buf)
        buf.append(pOut[0])
        buf.append(pOut[1])
        (status, backData, backLen) = self._tocard( 0x0C, buf)

        if (status == self.OK) and (backLen == 0x18):
            return  1
        else:
            return 0

# ------------------------------------------------------------------------------
    def SelectTag(self, uid):
        byte5 = 0
        
        #(status,puid)= self.anticoll(self.PICC_ANTICOLL1)
        #print("uid",uid,"puid",puid)
        for i in uid:
            byte5 = byte5 ^ i
        puid = uid + [byte5]
        
        if self.PcdSelect(puid,self.PICC_ANTICOLL1) == 0:
            return (self.ERR,[])
        return (self.OK , uid)
        
# ------------------------------------------------------------------------------
    def tohexstring(self,v):
        s="["
        for i in v:
            if i != v[0]:
                s = s+ ", "
            s=s+ "0x{:02X}".format(i)
        s= s+ "]"
        return s

# ------------------------------------------------------------------------------
    def SelectTagSN(self):
        valid_uid=[]
        (status,uid)= self.anticoll(self.PICC_ANTICOLL1)
        #print("Select Tag 1:",self.tohexstring(uid))
        if status != self.OK:
            return  (self.ERR,[])
        
        if self.DEBUG:   print("anticol(1) {}".format(uid))

        if self.PcdSelect(uid,self.PICC_ANTICOLL1) == 0:
            return (self.ERR,[])

        if self.DEBUG:   print("pcdSelect(1) {}".format(uid))
        
        #check if first byte is 0x88
        if uid[0] == 0x88 :
            #ok we have another type of card
            valid_uid.extend(uid[1:4])
            (status,uid)=self.anticoll(self.PICC_ANTICOLL2)
            #print("Select Tag 2:",self.tohexstring(uid))
            if status != self.OK:
                return (self.ERR,[])

            if self.DEBUG:
                print("Anticol(2) {}".format(uid))

            rtn =  self.PcdSelect(uid,self.PICC_ANTICOLL2)

            if self.DEBUG:
                print("pcdSelect(2) return={} uid={}".format(rtn,uid))
            
            if rtn == 0:
                return (self.ERR,[])

            if self.DEBUG:
                print("PcdSelect2() {}".format(uid))

            #now check again if uid[0] is 0x88
            if uid[0] == 0x88 :
                valid_uid.extend(uid[1:4])
                (status , uid) = self.anticoll(self.PICC_ANTICOLL3)

                if status != self.OK:
                    return (self.ERR,[])

                if self.DEBUG:
                    print("Anticol(3) {}".format(uid))
    
                if self.MFRC522_PcdSelect(uid,self.PICC_ANTICOLL3) == 0:
                    return (self.ERR,[])

                if self.DEBUG:
                    print("PcdSelect(3) {}".format(uid))

        valid_uid.extend(uid[0:5])
        
        # if we are here than the uid is ok
        # let's remove the last BYTE whic is the XOR sum
        return (self.OK , valid_uid[:len(valid_uid)-1])

# ------------------------------------------------------------------------------
    def auth(self, mode, addr, sect, ser):
        return self._tocard(0x0E, [mode, addr] + sect + ser[:4])[0]
    
# ------------------------------------------------------------------------------
    def authKeys(self,uid,addr,keyA=None, keyB=None):
        status = self.ERR
        if keyA is not None:
            status = self.auth(self.MIFARE_AUTHENT1A, addr, keyA, uid)
        elif keyB is not None:
            status = self.auth(self.MIFARE_AUTHENT1B, addr, keyB, uid)
        return status

# ------------------------------------------------------------------------------
    def stop_crypto1(self):
        self._cflags(0x08, 0x08)

# ------------------------------------------------------------------------------
    def read_sector_keyA(self, uid, sector, keyA=MIFARE_DEFAULT_KEY):
        data = read_data_block(reader, uid, sector, 3, keyA)
        return data[:6]

# ------------------------------------------------------------------------------
    def read(self, addr):
            data = [0x30, addr]
            data += self._crc(data)
            (stat, recv, _) = self._tocard(0x0C, data)
            return stat, recv

# ------------------------------------------------------------------------------
    def read_card_type(self, default_key=MIFARE_DEFAULT_KEY):
        """
        Determine the type of card based on sector and block access.
        """
        # Request card presence in idle mode
        status, bits = self.request(self.REQIDL)
        if status != self.OK:
            return None

        # Perform anticollision and retrieve UID
        status, uid = self.anticoll(self.PICC_ANTICOLL1)
        if status != self.OK:
            return None

        # Select the card
        status, uid = self.SelectTag(uid)
        if status != self.OK:
            return None

        # Attempt to identify the card type
        try:
            # Test for MIFARE Mini (5 sectors)
            for sector in range(5):
                if self.authKeys(uid, sector * 4, keyA=default_key) == self.OK:
                    continue
                else:
                    raise Exception("Not a Mini card.")

            return "Mini"

        except Exception:
            pass

        try:
            # Test for MIFARE Classic 1K (16 sectors)
            for sector in range(16):
                if self.authKeys(uid, sector * 4, keyA=default_key) == self.OK:
                    continue
                else:
                    raise Exception("Not a 1K card.")

            return "1K"

        except Exception:
            pass

        try:
            # Test for MIFARE Classic 4K (40 sectors)
            for sector in range(40):
                if self.authKeys(uid, sector * 4, keyA=default_key) == self.OK:
                    continue
                else:
                    raise Exception("Not a 4K card.")

            return "4K"

        except Exception:
            return None

# ------------------------------------------------------------------------------
    def dump_sector(self, sector):
        pass

# ------------------------------------------------------------------------------
    def dump_card(self):
        pass

# ------------------------------------------------------------------------------
    def write(self, addr, data):
        buf = [0xA0, addr]
        buf += self._crc(buf)
        (stat, recv, bits) = self._tocard(0x0C, buf)
 
        if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
            stat = self.ERR
        else:
            buf = []
            for i in range(16):
                buf.append(data[i])
            buf += self._crc(buf)
            (stat, recv, bits) = self._tocard(0x0C, buf)
            if not (stat == self.OK) or not (bits == 4) or not ((recv[0] & 0x0F) == 0x0A):
                stat = self.ERR
        return stat

# ------------------------------------------------------------------------------
    def writeSectorBlock(self,uid, sector, block, data, keyA=MIFARE_DEFAULT_KEY, keyB=MIFARE_DEFAULT_KEY):
        absoluteBlock =  sector * 4 + (block % 4)
        if absoluteBlock > 63 :
            return self.ERR
        if len(data) != 16:
            return self.ERR
        if self.authKeys(uid,absoluteBlock,keyA,keyB) != self.ERR :
            return self.write(absoluteBlock, data)
        return self.ERR
 
# ------------------------------------------------------------------------------
    def readSectorBlock(self, uid, sector, block, keyA=MIFARE_DEFAULT_KEY, keyB=MIFARE_DEFAULT_KEY):
        absoluteBlock =  sector * 4 + (block % 4)
        if absoluteBlock > 63 :
            return self.ERR, None
        if self.authKeys(uid,absoluteBlock,keyA,keyB) != self.ERR :
            return self.read(absoluteBlock)
        return self.ERR, None
 
# ------------------------------------------------------------------------------
    def MFRC522_DumpClassic1K(self,uid, Start=0, End=64, keyA=MIFARE_DEFAULT_KEY, keyB=MIFARE_DEFAULT_KEY):
        for absoluteBlock in range(Start,End):
            status = self.authKeys(uid,absoluteBlock,keyA,keyB)
            # Check if authenticated
            print("{:02d} S{:02d} B{:1d}: ".format(absoluteBlock, absoluteBlock//4 , absoluteBlock % 4),end="")
            if status == self.OK:                    
                status, block = self.read(absoluteBlock)
                if status == self.ERR:
                    break
                else:
                    for value in block:
                        print("{:02X} ".format(value),end="")
                    print("  ",end="")
                    for value in block:
                        if (value > 0x20) and (value < 0x7f):
                            print(chr(value),end="")
                        else:
                            print('.',end="")
                    print("")
            else:
                break
        if status == self.ERR:
            print("Authentication error")
            return self.ERR
        return self.OK

# ------------------------------------------------------------------------------
