from bleak import BleakClient
import asyncio

# Micro:bit UART UUIDs
UART_RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # TX to micro:bit

async def test_connection(address):
    try:
        async with BleakClient(address) as client:
            print(f"Connected: {client.is_connected}")
            await client.write_gatt_char(UART_RX_UUID, b"START:10")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_connection("E4:EE:A6:16:7E:B0"))