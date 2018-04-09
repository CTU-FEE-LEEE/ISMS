#!/usr/bin/python

#uncomment for debbug purposes
#import logging
#logging.basicConfig(level=logging.DEBUG)

import time
import datetime
import sys
import os
import minimalmodbus

from pymlab import config
from mlabutils import ejson

parser = ejson.Parser()

#### Functions ###############################################
def modBusInit():
    instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1) # port name, slave address (in decimal)

    instrument.serial.port          # this is the serial port name
    instrument.serial.baudrate = 9600   # Baud
    instrument.serial.bytesize = 8
    instrument.serial.stopbits = 2
    instrument.serial.timeout  = 0.5   # seconds

    instrument.mode = minimalmodbus.MODE_RTU # rtu or ascii mode
    return instrument

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
sys.stdout.write("Time, water-level,  temp1,  conduc, salinity, tds_kcl, temp2, pH, redox \r\n")
#sys.stdout.write("Time, channel #1,  channel #2,  channel #3 ,  channel #4,  channel #5  channel #6 ,  channel #7,  channel #8   \r\n")
sensor1 = cfg.get_device("current_sensor1")
#time.sleep(0.5)

#### Data Logging ###################################################

while True:
    try:
        # modbus
        instrument = modBusInit()
        before = time.time()-interval
        while True:
            
            filename = path + time.strftime("%Y%m%d%H", time.gmtime()) +"0000_"+ stationName + "_data.csv"        
            now = time.time()
            
            if (now - before >= interval - 2.5):     #   0.5*5 channels= 2.5s
                ##Measuremment settings
                sensor1.setADC(channel = 1, gain = 1, sample_rate = 3.75);
                
                instrument.address = 0x1E    # this is the slave address number (1E-conductivity)
                instrument.write_register(0x01, 0x1F, 0) # Registernumber, value, number of decimals for storage
                
                instrument.address = 0x14    # this is the slave address number (14 - pH)
                instrument.write_register(0x01, 0x1F, 0) # Registernumber, value, number of decimals for storage
                                
                time.sleep(0.5)

                ##Reading
                ## Read data from analog sensors ##
                channel1 = sensor1.readCurrent();
                channel1 = 0.2488*channel1-0.8892; # transformation from mA to meters

                ## Read data from conductivity sensor ##
                instrument.address = 0x1E    # this is the slave address number (1E-conductivity)

                temperature1 = instrument.read_float(0x53, 3, 2) # Registernumber, number of decimals                
                conductivity = instrument.read_float(0x55, 3, 2) # Registernumber, number of decimals                
                salinity = instrument.read_float(0x57, 3, 2) # Registernumber, number of decimals                
                tds_kcl = instrument.read_float(0x59, 3, 2) # Registernumber, number of decimals                
                
                ## Read data from pH sensor ##
                instrument.address = 0x14    # this is the slave address number (14 - pH)
                
                temperature2 = instrument.read_float(0x53, 3, 2) # Registernumber, number of decimals                
                pH = instrument.read_float(0x55, 3, 2) # Registernumber, number of decimals                
                redox = instrument.read_float(0x57, 3, 2) # Registernumber, number of decimals 
                
                with open(filename, "a") as f:
                    sys.stdout.write("%s \t %0.3f \t  %0.3f \t %0.3f \t %0.3f \t %0.3f \t %0.3f \t %0.3f \t %0.3f \t \n" % (datetime.datetime.now().isoformat(), channel1, temperature1, conductivity, salinity, tds_kcl, temperature2, pH, redox))

                    f.write("%d;%0.3f;%0.3f;%0.3f;%0.3f;%0.3f;%0.3f;%0.3f;%0.3f\n" % (time.time(), channel1, temperature1, conductivity, salinity, tds_kcl, temperature2, pH, redox))
                    f.flush()
                    sys.stdout.flush()
                    before = time.time()
                f.close()
                
            else:
                time.sleep(0.1)

    except KeyboardInterrupt:
        f.close()
        sys.exit(0)
    except Exception as e:
        print(e)
        time.sleep(5)


