#!/usr/bin/env python3
"""
MFRC522 RFID Reader/Writer
Read and write RFID/NFC cards and tags using MFRC522 module
"""

import time
import signal
import sys
import hashlib
import json
from datetime import datetime

# Import SPI support
try:
    import spidev
    SPI_AVAILABLE = True
except ImportError:
    SPI_AVAILABLE = False

from gpiozero import LED, Buzzer, Button

# MFRC522 SPI Configuration
RST_PIN = 22    # Reset pin
SPI_BUS = 0     # SPI bus
SPI_DEVICE = 0  # SPI device

# Optional I/O
LED_PIN = 23        # Status LED
BUZZER_PIN = 24     # Audio feedback
BUTTON_PIN = 25     # Mode select button

# MFRC522 Commands
MFRC522_IDLE = 0x00
MFRC522_AUTHENT = 0x0E
MFRC522_RECEIVE = 0x08
MFRC522_TRANSMIT = 0x04
MFRC522_TRANSCEIVE = 0x0C
MFRC522_RESETPHASE = 0x0F
MFRC522_CALCCRC = 0x03

# MFRC522 Registers
CommandReg = 0x01
CommIEnReg = 0x02
DivlEnReg = 0x03
CommIrqReg = 0x04
DivIrqReg = 0x05
ErrorReg = 0x06
Status1Reg = 0x07
Status2Reg = 0x08
FIFODataReg = 0x09
FIFOLevelReg = 0x0A
WaterLevelReg = 0x0B
ControlReg = 0x0C
BitFramingReg = 0x0D
CollReg = 0x0E

# Page 1: Command
ModeReg = 0x11
TxModeReg = 0x12
RxModeReg = 0x13
TxControlReg = 0x14
TxAutoReg = 0x15
TxSelReg = 0x16
RxSelReg = 0x17
RxThresholdReg = 0x18
DemodReg = 0x19
MfTxReg = 0x1C
MfRxReg = 0x1D
SerialSpeedReg = 0x1F

# Page 2: CFG
CRCResultRegM = 0x21
CRCResultRegL = 0x22
ModWidthReg = 0x24
RFCfgReg = 0x26
GsNReg = 0x27
CWGsPReg = 0x28
ModGsPReg = 0x29
TModeReg = 0x2A
TPrescalerReg = 0x2B
TReloadRegH = 0x2C
TReloadRegL = 0x2D
TCounterValueRegH = 0x2E
TCounterValueRegL = 0x2F

# Page 3: TestRegister
TestSel1Reg = 0x31
TestSel2Reg = 0x32
TestPinEnReg = 0x33
TestPinValueReg = 0x34
TestBusReg = 0x35
AutoTestReg = 0x36
VersionReg = 0x37
AnalogTestReg = 0x38
TestDAC1Reg = 0x39
TestDAC2Reg = 0x3A
TestADCReg = 0x3B

# PICC Commands
PICC_REQIDL = 0x26
PICC_REQALL = 0x52
PICC_ANTICOLL = 0x93
PICC_SElECTTAG = 0x93
PICC_AUTHENT1A = 0x60
PICC_AUTHENT1B = 0x61
PICC_READ = 0x30
PICC_WRITE = 0xA0
PICC_DECREMENT = 0xC0
PICC_INCREMENT = 0xC1
PICC_RESTORE = 0xC2
PICC_TRANSFER = 0xB0
PICC_HALT = 0x50

# Status codes
MI_OK = 0
MI_NOTAGERR = 1
MI_ERR = 2

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class MFRC522:
    """MFRC522 RFID reader/writer class"""
    
    def __init__(self, rst_pin=RST_PIN, spi_bus=SPI_BUS, spi_device=SPI_DEVICE):
        """
        Initialize MFRC522 RFID reader
        
        Args:
            rst_pin: Reset pin GPIO number
            spi_bus: SPI bus number
            spi_device: SPI device number
        """
        if not SPI_AVAILABLE:
            raise ImportError("spidev library not available. Install with: pip install spidev")
        
        self.rst_pin = rst_pin
        
        # Initialize SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 1000000
        
        # Initialize reset pin
        from gpiozero import OutputDevice
        self.reset_pin = OutputDevice(rst_pin)
        
        # Initialize the MFRC522
        self._init()
    
    def _init(self):
        """Initialize the MFRC522"""
        # Reset the chip
        self.reset_pin.off()
        time.sleep(0.01)
        self.reset_pin.on()
        time.sleep(0.05)
        
        # Configure the chip
        self._write_register(TModeReg, 0x8D)
        self._write_register(TPrescalerReg, 0x3E)
        self._write_register(TReloadRegL, 30)
        self._write_register(TReloadRegH, 0)
        self._write_register(TxAutoReg, 0x40)
        self._write_register(ModeReg, 0x3D)
        
        # Turn on antenna
        self._antenna_on()
    
    def _write_register(self, addr, val):
        """Write a byte to a register"""
        self.spi.xfer2([(addr << 1) & 0x7E, val])
    
    def _read_register(self, addr):
        """Read a byte from a register"""
        val = self.spi.xfer2([((addr << 1) & 0x7E) | 0x80, 0])
        return val[1]
    
    def _set_bit_mask(self, reg, mask):
        """Set register bit mask"""
        tmp = self._read_register(reg)
        self._write_register(reg, tmp | mask)
    
    def _clear_bit_mask(self, reg, mask):
        """Clear register bit mask"""
        tmp = self._read_register(reg)
        self._write_register(reg, tmp & (~mask))
    
    def _antenna_on(self):
        """Turn on antenna"""
        temp = self._read_register(TxControlReg)
        if not (temp & 0x03):
            self._set_bit_mask(TxControlReg, 0x03)
    
    def _antenna_off(self):
        """Turn off antenna"""
        self._clear_bit_mask(TxControlReg, 0x03)
    
    def _to_card(self, command, send_data):
        """Send data to card"""
        back_data = []
        back_len = 0
        status = MI_ERR
        irq_en = 0x00
        wait_irq = 0x00
        
        if command == MFRC522_AUTHENT:
            irq_en = 0x12
            wait_irq = 0x10
        if command == MFRC522_TRANSCEIVE:
            irq_en = 0x77
            wait_irq = 0x30
        
        self._write_register(CommIEnReg, irq_en | 0x80)
        self._clear_bit_mask(CommIrqReg, 0x80)
        self._set_bit_mask(FIFOLevelReg, 0x80)
        
        self._write_register(CommandReg, MFRC522_IDLE)
        
        # Write data to FIFO
        for i in range(len(send_data)):
            self._write_register(FIFODataReg, send_data[i])
        
        # Execute command
        self._write_register(CommandReg, command)
        if command == MFRC522_TRANSCEIVE:
            self._set_bit_mask(BitFramingReg, 0x80)
        
        # Wait for completion
        i = 2000
        while True:
            n = self._read_register(CommIrqReg)
            i -= 1
            if not ((i != 0) and not (n & 0x01) and not (n & wait_irq)):
                break
        
        self._clear_bit_mask(BitFramingReg, 0x80)
        
        if i != 0:
            if (self._read_register(ErrorReg) & 0x1B) == 0x00:
                status = MI_OK
                
                if n & irq_en & 0x01:
                    status = MI_NOTAGERR
                
                if command == MFRC522_TRANSCEIVE:
                    n = self._read_register(FIFOLevelReg)
                    last_bits = self._read_register(ControlReg) & 0x07
                    if last_bits != 0:
                        back_len = (n - 1) * 8 + last_bits
                    else:
                        back_len = n * 8
                    
                    if n == 0:
                        n = 1
                    if n > 16:
                        n = 16
                    
                    # Read data from FIFO
                    for i in range(n):
                        back_data.append(self._read_register(FIFODataReg))
            else:
                status = MI_ERR
        
        return (status, back_data, back_len)
    
    def request(self, req_mode):
        """Request card"""
        self._write_register(BitFramingReg, 0x07)
        
        (status, back_data, back_len) = self._to_card(MFRC522_TRANSCEIVE, [req_mode])
        
        if ((status != MI_OK) | (back_len != 0x10)):
            status = MI_ERR
        
        return (status, back_data)
    
    def anticoll(self):
        """Anti-collision detection"""
        back_data = []
        serial_number = []
        
        self._write_register(BitFramingReg, 0x00)
        
        serial_number.append(PICC_ANTICOLL)
        serial_number.append(0x20)
        
        (status, back_data, back_len) = self._to_card(MFRC522_TRANSCEIVE, serial_number)
        
        if status == MI_OK:
            i = 0
            if len(back_data) == 5:
                for i in range(4):
                    serial_number_check = serial_number_check ^ back_data[i]
                if serial_number_check != back_data[i]:
                    status = MI_ERR
            else:
                status = MI_ERR
        
        return (status, back_data)
    
    def calculate_crc(self, p_in_data):
        """Calculate CRC"""
        self._clear_bit_mask(DivIrqReg, 0x04)
        self._set_bit_mask(FIFOLevelReg, 0x80)
        
        # Write data to FIFO
        for i in range(len(p_in_data)):
            self._write_register(FIFODataReg, p_in_data[i])
        
        self._write_register(CommandReg, MFRC522_CALCCRC)
        
        # Wait for CRC calculation
        i = 0xFF
        while True:
            n = self._read_register(DivIrqReg)
            i -= 1
            if not ((i != 0) and not (n & 0x04)):
                break
        
        # Read CRC result
        p_out_data = []
        p_out_data.append(self._read_register(CRCResultRegL))
        p_out_data.append(self._read_register(CRCResultRegM))
        
        return p_out_data
    
    def select_tag(self, ser_num):
        """Select tag"""
        back_data = []
        buf = []
        buf.append(PICC_SElECTTAG)
        buf.append(0x70)
        
        for i in range(5):
            buf.append(ser_num[i])
        
        p_out = self.calculate_crc(buf)
        buf.append(p_out[0])
        buf.append(p_out[1])
        
        (status, back_data, back_len) = self._to_card(MFRC522_TRANSCEIVE, buf)
        
        if (status == MI_OK) and (back_len == 0x18):
            return 1
        else:
            return 0
    
    def auth(self, auth_mode, block_addr, sector_key, ser_num):
        """Authenticate"""
        buff = []
        
        # Validation
        buff.append(auth_mode)
        buff.append(block_addr)
        
        for i in range(len(sector_key)):
            buff.append(sector_key[i])
        
        for i in range(4):
            buff.append(ser_num[i])
        
        (status, back_data, back_len) = self._to_card(MFRC522_AUTHENT, buff)
        
        if not (status == MI_OK):
            print("AUTH ERROR!")
        if not (self._read_register(Status2Reg) & 0x08) != 0:
            print("AUTH ERROR(status2reg & 0x08) != 0")
        
        return status
    
    def stop_crypto1(self):
        """Stop crypto1"""
        self._clear_bit_mask(Status2Reg, 0x08)
    
    def read(self, block_addr):
        """Read block"""
        recv_data = []
        recv_data.append(PICC_READ)
        recv_data.append(block_addr)
        
        p_out = self.calculate_crc(recv_data)
        recv_data.append(p_out[0])
        recv_data.append(p_out[1])
        
        (status, back_data, back_len) = self._to_card(MFRC522_TRANSCEIVE, recv_data)
        
        if not (status == MI_OK):
            print("Error while reading!")
        
        if len(back_data) == 16:
            return back_data
        else:
            return None
    
    def write(self, block_addr, write_data):
        """Write block"""
        buff = []
        buff.append(PICC_WRITE)
        buff.append(block_addr)
        
        crc = self.calculate_crc(buff)
        buff.append(crc[0])
        buff.append(crc[1])
        
        (status, back_data, back_len) = self._to_card(MFRC522_TRANSCEIVE, buff)
        
        if not (status == MI_OK) or not (back_len == 4) or not ((back_data[0] & 0x0F) == 0x0A):
            status = MI_ERR
        
        if status == MI_OK:
            buf = []
            for i in range(16):
                buf.append(write_data[i])
            
            crc = self.calculate_crc(buf)
            buf.append(crc[0])
            buf.append(crc[1])
            
            (status, back_data, back_len) = self._to_card(MFRC522_TRANSCEIVE, buf)
            
            if not (status == MI_OK) or not (back_len == 4) or not ((back_data[0] & 0x0F) == 0x0A):
                print("Error while writing")
                status = MI_ERR
        
        return status
    
    def get_version(self):
        """Get MFRC522 version"""
        return self._read_register(VersionReg)
    
    def cleanup(self):
        """Clean up resources"""
        self._antenna_off()
        self.spi.close()
        self.reset_pin.close()

class RFIDCardManager:
    """High-level RFID card management"""
    
    def __init__(self, rfid_reader):
        """
        Initialize card manager
        
        Args:
            rfid_reader: MFRC522 instance
        """
        self.reader = rfid_reader
        self.default_key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        
        # Card database (in real application, use proper database)
        self.card_database = {}
        self.load_database()
    
    def load_database(self):
        """Load card database from file"""
        try:
            with open('rfid_cards.json', 'r') as f:
                self.card_database = json.load(f)
        except FileNotFoundError:
            self.card_database = {}
    
    def save_database(self):
        """Save card database to file"""
        with open('rfid_cards.json', 'w') as f:
            json.dump(self.card_database, f, indent=2)
    
    def wait_for_card(self, timeout=None):
        """
        Wait for card to be presented
        
        Args:
            timeout: Timeout in seconds (None for infinite)
            
        Returns:
            Card UID as string or None if timeout
        """
        start_time = time.time()
        
        while True:
            if timeout and (time.time() - start_time) > timeout:
                return None
            
            # Request card
            (status, TagType) = self.reader.request(PICC_REQIDL)
            
            if status == MI_OK:
                # Get UID
                (status, uid) = self.reader.anticoll()
                
                if status == MI_OK:
                    # Convert UID to string
                    uid_string = "-".join([f"{x:02X}" for x in uid[:4]])
                    return uid_string
            
            time.sleep(0.1)
    
    def read_card_data(self, uid_string, block=4):
        """
        Read data from card
        
        Args:
            uid_string: Card UID
            block: Block number to read
            
        Returns:
            Data as string or None if error
        """
        try:
            # Convert UID back to bytes
            uid = [int(x, 16) for x in uid_string.split("-")]
            
            # Select card
            if not self.reader.select_tag(uid):
                return None
            
            # Authenticate
            status = self.reader.auth(PICC_AUTHENT1A, block, self.default_key, uid)
            if status != MI_OK:
                return None
            
            # Read block
            data = self.reader.read(block)
            if data:
                # Convert to string (remove null bytes)
                text = ''.join([chr(x) for x in data if x != 0])
                return text
            
            return None
            
        except Exception as e:
            print(f"Error reading card: {e}")
            return None
        finally:
            self.reader.stop_crypto1()
    
    def write_card_data(self, uid_string, data, block=4):
        """
        Write data to card
        
        Args:
            uid_string: Card UID
            data: String data to write (max 16 chars)
            block: Block number to write
            
        Returns:
            True if successful
        """
        try:
            # Convert UID back to bytes
            uid = [int(x, 16) for x in uid_string.split("-")]
            
            # Select card
            if not self.reader.select_tag(uid):
                return False
            
            # Authenticate
            status = self.reader.auth(PICC_AUTHENT1A, block, self.default_key, uid)
            if status != MI_OK:
                return False
            
            # Prepare data (pad to 16 bytes)
            write_data = [0] * 16
            for i, char in enumerate(data[:16]):
                write_data[i] = ord(char)
            
            # Write block
            status = self.reader.write(block, write_data)
            return status == MI_OK
            
        except Exception as e:
            print(f"Error writing card: {e}")
            return False
        finally:
            self.reader.stop_crypto1()
    
    def register_card(self, uid_string, name, access_level="user"):
        """Register a new card in database"""
        self.card_database[uid_string] = {
            'name': name,
            'access_level': access_level,
            'registered': datetime.now().isoformat(),
            'last_seen': None,
            'use_count': 0
        }
        self.save_database()
    
    def get_card_info(self, uid_string):
        """Get card information from database"""
        return self.card_database.get(uid_string, None)
    
    def update_card_access(self, uid_string):
        """Update card access statistics"""
        if uid_string in self.card_database:
            self.card_database[uid_string]['last_seen'] = datetime.now().isoformat()
            self.card_database[uid_string]['use_count'] += 1
            self.save_database()

def basic_card_reading():
    """Basic card reading demonstration"""
    print("\n=== Basic RFID Card Reading ===")
    print("Present RFID card to reader")
    print("Press Ctrl+C to exit")
    
    if not SPI_AVAILABLE:
        print("Error: SPI library not available")
        print("Install with: pip install spidev")
        return
    
    try:
        reader = MFRC522()
        card_manager = RFIDCardManager(reader)
        
        try:
            status_led = LED(LED_PIN)
            buzzer = Buzzer(BUZZER_PIN)
            has_feedback = True
        except:
            has_feedback = False
            print("Note: No LED/buzzer connected for feedback")
        
        version = reader.get_version()
        print(f"MFRC522 version: 0x{version:02X}")
        
        cards_read = 0
        
        while True:
            uid = card_manager.wait_for_card(timeout=0.5)
            
            if uid:
                cards_read += 1
                print(f"\n📱 Card {cards_read} detected!")
                print(f"UID: {uid}")
                
                # Feedback
                if has_feedback:
                    status_led.on()
                    buzzer.beep(0.1, 0.1, n=1)
                
                # Try to read data from card
                data = card_manager.read_card_data(uid)
                if data:
                    print(f"Data: '{data}'")
                else:
                    print("No readable data on card")
                
                # Check database
                card_info = card_manager.get_card_info(uid)
                if card_info:
                    print(f"Known card: {card_info['name']} ({card_info['access_level']})")
                    print(f"Uses: {card_info['use_count']}")
                    card_manager.update_card_access(uid)
                else:
                    print("Unknown card")
                
                if has_feedback:
                    status_led.off()
                
                time.sleep(1)  # Prevent multiple reads
            else:
                print("\rWaiting for card...", end='')
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if has_feedback:
            status_led.close()
            buzzer.close()
        reader.cleanup()

def access_control_system():
    """RFID access control demonstration"""
    print("\n=== RFID Access Control System ===")
    print("Present authorized cards for access")
    print("Press Ctrl+C to exit")
    
    if not SPI_AVAILABLE:
        print("Error: SPI library not available")
        return
    
    try:
        reader = MFRC522()
        card_manager = RFIDCardManager(reader)
        
        try:
            status_led = LED(LED_PIN)
            buzzer = Buzzer(BUZZER_PIN)
            has_feedback = True
        except:
            has_feedback = False
        
        access_attempts = 0
        successful_access = 0
        
        while True:
            uid = card_manager.wait_for_card(timeout=0.5)
            
            if uid:
                access_attempts += 1
                card_info = card_manager.get_card_info(uid)
                
                if card_info:
                    # Authorized card
                    successful_access += 1
                    print(f"\n✅ ACCESS GRANTED")
                    print(f"Welcome, {card_info['name']}!")
                    print(f"Access level: {card_info['access_level']}")
                    
                    if has_feedback:
                        status_led.blink(0.2, 0.2, n=3)
                        buzzer.beep(0.1, 0.1, n=2)
                    
                    card_manager.update_card_access(uid)
                    
                else:
                    # Unauthorized card
                    print(f"\n❌ ACCESS DENIED")
                    print(f"Unknown card: {uid}")
                    
                    if has_feedback:
                        status_led.blink(0.05, 0.05, n=10)
                        buzzer.beep(0.05, 0.05, n=5)
                
                print(f"Session stats: {successful_access}/{access_attempts} successful")
                time.sleep(2)
            else:
                print(f"\rAccess Control Active - {successful_access}/{access_attempts} granted", end='')
    
    except KeyboardInterrupt:
        print(f"\n\nSession Summary:")
        print(f"Access attempts: {access_attempts}")
        print(f"Successful: {successful_access}")
        print(f"Denied: {access_attempts - successful_access}")
    finally:
        if has_feedback:
            status_led.close()
            buzzer.close()
        reader.cleanup()

def card_registration_system():
    """Card registration and management"""
    print("\n=== RFID Card Registration ===")
    print("Register new cards in the system")
    print("Press Ctrl+C to exit")
    
    if not SPI_AVAILABLE:
        print("Error: SPI library not available")
        return
    
    try:
        reader = MFRC522()
        card_manager = RFIDCardManager(reader)
        
        while True:
            print("\n1. Register new card")
            print("2. List registered cards")
            print("3. Delete card")
            print("4. Write data to card")
            print("5. Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                print("\nPresent card to register...")
                uid = card_manager.wait_for_card(timeout=10)
                
                if uid:
                    if card_manager.get_card_info(uid):
                        print(f"Card {uid} is already registered!")
                    else:
                        name = input("Enter card holder name: ").strip()
                        access_level = input("Enter access level (user/admin) [user]: ").strip() or "user"
                        
                        card_manager.register_card(uid, name, access_level)
                        print(f"✅ Card registered: {name} ({access_level})")
                else:
                    print("❌ No card detected within timeout")
            
            elif choice == '2':
                print("\n📋 Registered Cards:")
                if card_manager.card_database:
                    for uid, info in card_manager.card_database.items():
                        print(f"  {uid}: {info['name']} ({info['access_level']}) - Used {info['use_count']} times")
                else:
                    print("  No cards registered")
            
            elif choice == '3':
                uid = input("Enter card UID to delete: ").strip()
                if uid in card_manager.card_database:
                    del card_manager.card_database[uid]
                    card_manager.save_database()
                    print(f"✅ Card {uid} deleted")
                else:
                    print(f"❌ Card {uid} not found")
            
            elif choice == '4':
                print("\nPresent card to write data...")
                uid = card_manager.wait_for_card(timeout=10)
                
                if uid:
                    data = input("Enter data to write (max 16 chars): ")[:16]
                    if card_manager.write_card_data(uid, data):
                        print("✅ Data written successfully")
                    else:
                        print("❌ Failed to write data")
                else:
                    print("❌ No card detected")
            
            elif choice == '5':
                break
    
    except KeyboardInterrupt:
        pass
    finally:
        reader.cleanup()

def card_cloning_demo():
    """Demonstrate reading and cloning card data"""
    print("\n=== RFID Card Cloning Demo ===")
    print("⚠️ For educational purposes only!")
    print("Read data from one card and write to another")
    print("Press Ctrl+C to exit")
    
    if not SPI_AVAILABLE:
        print("Error: SPI library not available")
        return
    
    try:
        reader = MFRC522()
        card_manager = RFIDCardManager(reader)
        
        # Step 1: Read source card
        print("\nStep 1: Present SOURCE card to read...")
        source_uid = card_manager.wait_for_card(timeout=15)
        
        if not source_uid:
            print("❌ No source card detected")
            return
        
        print(f"📖 Reading from card: {source_uid}")
        
        # Read multiple blocks
        source_data = {}
        for block in [4, 5, 6]:  # Safe blocks to read
            data = card_manager.read_card_data(source_uid, block)
            if data:
                source_data[block] = data
                print(f"Block {block}: '{data}'")
        
        if not source_data:
            print("❌ No data could be read from source card")
            return
        
        # Step 2: Write to destination card
        print(f"\nStep 2: Present DESTINATION card to write...")
        print("⚠️ This will overwrite existing data!")
        confirm = input("Continue? (yes/no): ").lower()
        
        if confirm != 'yes':
            print("❌ Operation cancelled")
            return
        
        dest_uid = card_manager.wait_for_card(timeout=15)
        
        if not dest_uid:
            print("❌ No destination card detected")
            return
        
        if dest_uid == source_uid:
            print("❌ Cannot clone to the same card!")
            return
        
        print(f"📝 Writing to card: {dest_uid}")
        
        # Write data to destination
        success_count = 0
        for block, data in source_data.items():
            if card_manager.write_card_data(dest_uid, data, block):
                print(f"✅ Block {block} written successfully")
                success_count += 1
            else:
                print(f"❌ Failed to write block {block}")
        
        print(f"\n🎯 Cloning complete: {success_count}/{len(source_data)} blocks copied")
        
        # Verify by reading destination
        print("\nStep 3: Verifying destination card...")
        for block in source_data.keys():
            data = card_manager.read_card_data(dest_uid, block)
            if data == source_data[block]:
                print(f"✅ Block {block} verified: '{data}'")
            else:
                print(f"❌ Block {block} verification failed")
    
    except KeyboardInterrupt:
        pass
    finally:
        reader.cleanup()

def attendance_system():
    """RFID-based attendance tracking system"""
    print("\n=== RFID Attendance System ===")
    print("Track employee/student attendance")
    print("Press Ctrl+C to exit")
    
    if not SPI_AVAILABLE:
        print("Error: SPI library not available")
        return
    
    try:
        reader = MFRC522()
        card_manager = RFIDCardManager(reader)
        
        # Attendance log (in real system, use database)
        attendance_log = []
        
        def log_attendance(uid, name, action):
            entry = {
                'uid': uid,
                'name': name,
                'action': action,
                'timestamp': datetime.now().isoformat()
            }
            attendance_log.append(entry)
            
            # Save to file
            with open('attendance.json', 'w') as f:
                json.dump(attendance_log, f, indent=2)
        
        # Track who's currently present
        present_users = set()
        
        while True:
            uid = card_manager.wait_for_card(timeout=0.5)
            
            if uid:
                card_info = card_manager.get_card_info(uid)
                
                if card_info:
                    name = card_info['name']
                    
                    if uid in present_users:
                        # Check out
                        present_users.remove(uid)
                        action = "CHECK_OUT"
                        status = "👋 Goodbye"
                    else:
                        # Check in
                        present_users.add(uid)
                        action = "CHECK_IN"
                        status = "👋 Welcome"
                    
                    print(f"\n{status}, {name}!")
                    print(f"Action: {action}")
                    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
                    
                    # Log attendance
                    log_attendance(uid, name, action)
                    card_manager.update_card_access(uid)
                    
                else:
                    print(f"\n❌ Unregistered card: {uid}")
                
                # Show current status
                print(f"Currently present: {len(present_users)} people")
                if present_users:
                    present_names = [card_manager.get_card_info(u)['name'] for u in present_users]
                    print(f"Present: {', '.join(present_names)}")
                
                time.sleep(1)
            else:
                print(f"\rAttendance System Active - {len(present_users)} present", end='')
    
    except KeyboardInterrupt:
        print(f"\n\nAttendance Summary:")
        print(f"Total logs: {len(attendance_log)}")
        print(f"Currently present: {len(present_users)}")
    finally:
        reader.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("MFRC522 RFID Reader/Writer")
    print("==========================")
    print("SPI Configuration:")
    print(f"  RST: GPIO{RST_PIN}")
    print(f"  SPI Bus: {SPI_BUS}")
    print(f"  SPI Device: {SPI_DEVICE}")
    
    if not SPI_AVAILABLE:
        print("\n⚠️ Warning: SPI library not available")
        print("Install with: pip install spidev")
        print("Enable SPI: sudo raspi-config → Interface → SPI")
        return
    
    while True:
        print("\n\nSelect Function:")
        print("1. Basic card reading")
        print("2. Access control system")
        print("3. Card registration")
        print("4. Card cloning demo")
        print("5. Attendance system")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            basic_card_reading()
        elif choice == '2':
            access_control_system()
        elif choice == '3':
            card_registration_system()
        elif choice == '4':
            card_cloning_demo()
        elif choice == '5':
            attendance_system()
        elif choice == '6':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()