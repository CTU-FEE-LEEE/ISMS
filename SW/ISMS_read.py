#!/usr/bin/python

#uncomment for debbug purposes
#import logging
#logging.basicConfig(level=logging.DEBUG)

import time
import datetime
import sys
import os
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import struct

from pymlab import config
from mlabutils import ejson

parser = ejson.Parser()

#### Functions ###############################################
def modBusInit():
    client = ModbusClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, stopbits = 2, bytesize = 8, parity = 'N', timeout = 0.5)
    client.connect()
    return client

def reg2val(result):
    packed_string = struct.pack("HH", *(result.registers[1],result.registers[0]))
    value = struct.unpack("f", packed_string)[0]
    return value

#### Script Arguments ###############################################

if len(sys.argv) != 3:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s PORT_ADDRESS CONFIG_FILE\n" % (sys.argv[0], ))
    sys.exit(1)


port = eval(sys.argv[1])

value = parser.parse_file(sys.argv[2])
path = value['data_path']
interval = value['raw_sample_interval']
stationName = value['origin']

if (interval<5) or (interval>3600):
    sys.stderr.write("Invalid sample interval arguments.\n")
    sys.stderr.write("The interval has to be in the range from 5 to 3600 seconds\n")
    sys.exit(2)

#### Sensor Configuration ###########################################
# I2C
cfg = config.Config(
    i2c = {
            "port": port,
    },
    bus = [
        {
            "name":          "current_sensor1",
            "type":        "vcai2c01",
            "address":        0x68,
        },
    ],
)
cfg.initialize()

sys.stdout.write("Current loop and modbus sensor example \r\n")
sys.stdout.write("Time, water-level,  temp1,  conduc, salinity, tds_kcl, temp2, pH, redox, H_con \r\n")
#sys.stdout.write("Time, channel #1,  channel #2,  channel #3 ,  channel #4,  channel #5  channel #6 ,  channel #7,  channel #8   \r\n")
sensor1 = cfg.get_device("current_sensor1")
#time.sleep(0.5)

#### Data Logging ###################################################

while True:
    try:
        before = time.time()-interval
        while True:

            filename = path + time.strftime("%Y%m%d%H", time.gmtime()) +"0000_"+ stationName + "_data.csv"
            now = time.time()

            if (now - before >= interval - 2.5):     #   0.5*5 channels= 2.5s
                ##Measuremment settings
                sensor1.setADC(channel = 1, gain = 1, sample_rate = 3.75);

                time.sleep(0.5)

                ##Reading
                ## Read data from analog sensor ##
                channel1 = sensor1.readCurrent();
                channel1 = (0.2488*channel1-0.8892) + 185.522; # transformation from mA to meters and add current altitude of sensor in meters

                ## Read data from conductivity sensor ##
                for i in range(0,100):
                    try:
                        client = modBusInit()
                        UNIT = 0x1E # sensor address
                        rq = client.write_register(address = 0x01, value = 0x1F, unit = UNIT) # measure data
                        time.sleep(0.5)
                        # read data:
                        temperature = reg2val(client.read_holding_registers(address = 0x53, count = 2, unit = UNIT))
                        conductivity = reg2val(client.read_holding_registers(address = 0x55, count = 2, unit = UNIT))
                        salinity = reg2val(client.read_holding_registers(address = 0x57, count = 2, unit = UNIT))
                        tds_kcl = reg2val(client.read_holding_registers(address = 0x59, count = 2, unit = UNIT))

                        client.close()
                        break

                    except Exception as e:
                        print(str(e))
                        print(str(i))
                        client.close()
                        if i == 99:
                            print("Cannot read from conductivity probe")
                            temperature = 0
                            conductivity = 0
                            salinity = 0
                            tds_kcl = 0
                            break
                        time.sleep(2)

                time.sleep(0.5)
                ## Read data from pH sensor ##
                for i in range(0,100):
                    try:
                        client = modBusInit()
                        UNIT = 0x14 # sensor address
                        rq = client.write_register(address = 0x01, value = 0x1F, unit = UNIT) # measure data
                        time.sleep(0.5)
                        # read data:
                        temperature2 = reg2val(client.read_holding_registers(address = 0x53, count = 2, unit = UNIT))
                        pH = reg2val(client.read_holding_registers(address = 0x55, count = 2, unit = UNIT))
                        redox = reg2val(client.read_holding_registers(address = 0x57, count = 2, unit = UNIT))

                        client.close()
                        break

                    except Exception as e:
                        print(str(e))
                        print(str(i))
                        client.close()
                        if i == 99:
                            print("Cannot read from pH probe")
                            temperature2 = 0
                            pH = 0
                            redox = 0
                            break
                        time.sleep(2)

                time.sleep(0.5)

                instrument.address = 0x14    # this is the slave address number (14 - pH)

                temperature2 = instrument.read_float(0x53, 3, 2) # Registernumber, number of decimals
                pH = instrument.read_float(0x55, 3, 2) # Registernumber, number of decimals
                redox = instrument.read_float(0x57, 3, 2) # Registernumber, number of decimals

                ## Read data from analog sensor ##
                sensor1.setADC(channel = 2, gain = 1, sample_rate = 3.75);
                time.sleep(0.5)
                channel2 = sensor1.readCurrent();
                if channel2 < 3:
                    channel2 = -1

                if channel2 >= 3 and channel2 <= 4:
                    channel2 = 0

                if channel2 > 4:
                    channel2 = (6.25*channel2-25); # transformation from mA to % of H concentration

                with open(filename, "a") as f:
                    sys.stdout.write("%s \t %0.3f \t  %0.3f \t %0.3f \t %0.3f \t %0.3f \t %0.3f \t %0.3f \t %0.3f \t %0.3f \t \n" % (datetime.datetime.now().isoformat(), channel1, temperature1, conductivity, salinity, tds_kcl, temperature2, pH, redox, channel2))

                    f.write("%d;%0.3f;%0.3f;%0.3f;%0.3f;%0.3f;%0.3f;%0.3f;%0.3f;%0.3f\n" % (time.time(), channel1, temperature1, conductivity, salinity, tds_kcl, temperature2, pH, redox, channel2))
                    f.flush()
                    sys.stdout.flush()
                    os.fsync(f.fileno())
                    before = time.time()
                f.close()

            else:
                time.sleep(0.1)

    except KeyboardInterrupt:
        f.close()
        sys.exit(0)
    except Exception as e:
        print(e)
        time.sleep(10)
