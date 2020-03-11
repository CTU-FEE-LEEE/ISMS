#!/usr/bin/env python
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time
import struct

def reg2val(result):
    packed_string = struct.pack("HH", *(result.registers[1],result.registers[0]))
    value = struct.unpack("f", packed_string)[0]
    return value


client = ModbusClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, stopbits = 2, bytesize = 8, parity = 'N', timeout = 0.5)
client.connect()

for i in range(0,100):
    try:
        UNIT = 0x1E
        rq = client.write_register(address = 0x01, value = 0x1F, unit = UNIT)
        time.sleep(0.5)

        result = client.read_holding_registers(address = 0x53, count = 2, unit = UNIT)
        temperature = reg2val(result)
        result = client.read_holding_registers(address = 0x55, count = 2, unit = UNIT)
        conductivity = reg2val(result)
        result = client.read_holding_registers(address = 0x57, count = 2, unit = UNIT)
        salinity = reg2val(result)
        result = client.read_holding_registers(address = 0x59, count = 2, unit = UNIT)
        tds_kcl = reg2val(result)

        print(temperature)
        print(conductivity)
        print(salinity)
        print(tds_kcl)
        client.close()
        break

    except Exception as e:
        print(str(e))
        print(str(i))
        if i == 99:
            print("Cannot read from conductivity probe")
            temperature = 0
            conductivity = 0
            salinity = 0
            tds_kcl = 0
            break
        time.sleep(2)
