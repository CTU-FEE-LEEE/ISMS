from pyModbusTCP.client import ModbusClient
import time
import sys

from mlabutils import ejson
parser = ejson.Parser()


#### Script Arguments ###############################################

if len(sys.argv) != 2:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s CONFIG_FILE\n" % (sys.argv[0], ))
    sys.exit(1)

value = parser.parse_file(sys.argv[1])
path = value['data_path'] # raw data
interval = value['meteo_sample_interval'] # raw data
stationName = value['origin']


#### Declaration ###############################################

# List of sensors
# ModBus address, Sensor type, Quantity
sensors = [ [1001,'Wind direction','deg'],
            [1002,'Wind speed','m/s'],
            [1003,'Gusty wind','m/s'],
            [1004,'Precipitation','mm'],
            [1005,'Temperature','C'],
            [1006,'Humidity','%'],
            [1007,'Atmospheric pressure','hPa'],
            [1008,'Solar exposure','W/m2'],
            [1009,'Dew point','C'],
            [1010,'Apparent temperature','C'],
                                                ]

#module init (with accessor functions)
c = ModbusClient()
c.host("192.168.55.56")
c.port(502)

#### Function definition ###############################################

# get data based on the list of sensors
def getData(sensors):
        # delete list
        lst = []        
        c.open()
        
        for i in range(len(sensors)):
            # Read 16 bits registers:
            regs = c.read_holding_registers(sensors[i][0], 1)            
            if regs:
                lst.append(float(regs[0])/10)
                print(sensors[i][1] + ": " + str(float(regs[0])/10) + " " + sensors[i][2])
            else:                
                lst[:] = []
                c.close()
                break
        c.close()
        return lst

# save file
def saveFile(filename,lst):
    with open(filename, "a") as f:
        f.write("%d;%0.1f;%0.1f;%0.1f;%0.1f;%0.1f;%0.1f;%0.1f;%0.1f;%0.1f;%0.1f\n"
            %(time.time(),lst[0],lst[1],lst[2],lst[3],lst[4],lst[5],lst[6],lst[7],lst[8],lst[9]))
        f.flush()
        os.fsync(f.fileno())
    f.close()
    
    
#### Main Procedure ###############################################

while(1):
    try:        
        # get data to list
        lst = getData(sensors)

        # create file name + path
        filename = path + time.strftime("%Y%m%d%H", time.gmtime()) + "0000_" + stationName + "_meteo.csv"

        # save file
        if not lst:
            print("ModBus TCP read error")
        else:
            saveFile(filename,lst)            
        
        # delete list
        lst[:] = []

        print("")

        #sleep first - ready for keyboard interrupt
        time.sleep(interval)
        
    except KeyboardInterrupt:
        print(" Keyboard interrupt - Closing")
        break
    except Exception as e:
        print("Unexpected error")
        print(e)
        time.sleep(interval)
    
