#!/usr/bin/env python
import minimalmodbus
import time

instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1) # port name, slave address (in decimal)

instrument.serial.port          # this is the serial port name
instrument.serial.baudrate = 9600   # Baud
instrument.serial.bytesize = 8
instrument.serial.stopbits = 2
instrument.serial.timeout  = 0.5   # seconds

instrument.address = 0x1E    # this is the slave address number
instrument.mode = minimalmodbus.MODE_RTU   # rtu or ascii mode
instrument.close_port_after_each_call = True

for i in range(0,100):
    try:
        instrument.write_register(0x01, 0x1F, 0) # Registernumber, value, number of decimals for storage

        time.sleep(0.5)

        ## Read temperature (PV = ProcessValue) ##
        temperature = instrument.read_float(0x53, 3, 2) # Registernumber, number of decimals
        print temperature
        conductivity = instrument.read_float(0x55, 3, 2) # Registernumber, number of decimals
        print conductivity
        salinity = instrument.read_float(0x57, 3, 2) # Registernumber, number of decimals
        print salinity
        tds_kcl = instrument.read_float(0x59, 3, 2) # Registernumber, number of decimals
        print tds_kcl

        print("")
        break

    except Exception as e:
        print(str(e))
        if i == 99:
            print("Cannot read from conductivity probe")
            temperature = 0
            conductivity = 0
            salinity = 0
            tds_kcl = 0
            break
        time.sleep(0.5+0.02*i)


## Change temperature setpoint (SP) ##
