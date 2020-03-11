#!/usr/bin/env python
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time
import struct

UNIT = 0x1

client = ModbusClient(method='rtu', port='/dev/ttyUSB0', timeout = 0.5, stopbits = 2, bytesize = 8, parity = 'N')
client.connect()

UNIT = 0x1E
rq = client.write_register(address = 0x01, value = 0x1F, unit = UNIT)
time.sleep(0.5)

result0 = client.read_holding_registers(address = 0x53, count = 2, unit = UNIT)
packed_string = struct.pack("HH", *(result0.registers[1],result0.registers[0]))
value = struct.unpack("f", packed_string)[0]
print(value)
