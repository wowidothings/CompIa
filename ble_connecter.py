from PyQt6.QtCore import QThread, pyqtSignal
from bleak import BleakClient
import asyncio

class BLEWorker(QThread):
    data_received = pyqtSignal(str)
    connected = pyqtSignal(bool)

    def __init__(self, address):
        super().__init__()
        self.address = address
        self.duration = 10
        self.is_running = False

    def set_duration(self, duration):
        self.duration = duration

    async def main_ble(self):
        try:
            async with BleakClient(self.address) as client:
                self.connected.emit(True)
                await client.write_gatt_char("6e400002-b5a3-f393-e0a9-e50e24dcca9e", f"START:{self.duration}".encode())
                
                start_time = asyncio.get_event_loop().time()
                while (asyncio.get_event_loop().time() - start_time) < self.duration:
                    raw_data = await client.read_gatt_char("6e400003-b5a3-f393-e0a9-e50e24dcca9e")
                    self.data_received.emit(raw_data.decode().strip())
                    await asyncio.sleep(0.02)
        except Exception as e:
            print(f"BLE Error: {e}")
        finally:
            self.connected.emit(False)

    def run(self):
        asyncio.run(self.main_ble())