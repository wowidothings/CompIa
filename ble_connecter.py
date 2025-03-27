# ble_connector.py
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
from bleak import BleakClient, BleakScanner
import asyncio

# Micro:bit BLE UART Service UUIDs
UART_TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # RX (micro:bit → PC)
UART_RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # TX (PC → micro:bit)

class BLEWorker(QThread):
    data_received = pyqtSignal(str)    # Signal for incoming data
    connection_changed = pyqtSignal(bool)  # Connection status
    error_occurred = pyqtSignal(str)   # Error messages

    def __init__(self, address):
        super().__init__()
        self.address = address.upper()  # BLE addresses are case-insensitive
        self.client = BleakClient(self.address)
        self.duration = 10
        self.is_connected = False

    @pyqtSlot(int)
    def set_duration(self, duration):
        """Update collection duration from GUI input"""
        self.duration = duration

    async def _connect(self):
        """Establish BLE connection programmatically"""
        try:
            await self.client.connect()
            self.is_connected = True
            self.connection_changed.emit(True)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Connection failed: {str(e)}")
            return False

    async def _run_ble(self):
        """Main BLE communication loop"""
        if await self._connect():
            try:
                # Send START command with duration
                await self.client.write_gatt_char(
                    UART_RX_UUID, 
                    f"START:{self.duration}".encode(),
                    response=True
                )
                
                # Continuous data reading
                while self.is_connected:
                    raw_data = await self.client.read_gatt_char(UART_TX_UUID)
                    self.data_received.emit(raw_data.decode().strip())
                    await asyncio.sleep(0.01)
                    
            except Exception as e:
                self.error_occurred.emit(f"BLE error: {str(e)}")
            finally:
                await self.client.disconnect()
                self.connection_changed.emit(False)
                self.is_connected = False

    def run(self):
        """QThread entry point"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._run_ble())

    def stop(self):
        """Graceful shutdown"""
        if self.is_connected:
            asyncio.run_coroutine_threadsafe(
                self.client.disconnect(), 
                asyncio.get_event_loop()
            )