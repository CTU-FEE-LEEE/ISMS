#!/usr/bin/python
import hid
import time
import datetime
from time import sleep
import os, sys

from mlabutils import ejson

parser = ejson.Parser()

#### Script Arguments ###############################################

if len(sys.argv) != 2:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s CONFIG_FILE\n" % (sys.argv[0], ))
    sys.exit(1)

value = parser.parse_file(sys.argv[1])
path = value['data_upload']
stationName = value['origin']

def main():

    while True:

        print "Opening device"
        h = hid.device()
        h.open(0x10C4, 0xEA90)

        print "Manufacturer: %s" % h.get_manufacturer_string()
        print "Product: %s" % h.get_product_string()
        print "Serial No: %s" % h.get_serial_number_string()

        h.write([0x02, 0b00000110, 0x00, 0x00, 0x00]) # setup io pin direction 
        sleep( 1.00 )

        response = h.get_feature_report(0x03,2)
        previous_inputs = response[1]

        try:

            while True:
                response = h.get_feature_report(0x03,2)
                inputs = response[1]

                print bin(inputs) 

                now = datetime.datetime.now()
                filename = path + time.strftime("%Y%m%d%H", time.gmtime())+"0000_"+stationName+"_meta.csv"

                if not os.path.exists(filename):
                    with open(filename, "a") as f:
                        f.write('#timestamp,IO_state \n')
                        f.write("%.1f,%s\n" % (time.time(), hex(inputs)))

                if (previous_inputs != inputs):
                    with open(filename, "a") as f:
                        f.write("%.1f,%s\n" % (time.time(), hex(inputs)))
                        previous_inputs = inputs

                if not (inputs & 0b00000001) and  (0b00000001):
                    h.write([0x04, 0x00, 0xFF])
                    time.sleep(0.8)
                    h.write([0x04, 0xFF, 0xFF])
                    time.sleep(0.5)

                time.sleep(0.5)

        except IOError, ex:
            print ex

        except KeyboardInterrupt:
            print "Closing device"
            h.close()
            exit()

        print "Done"


if __name__ == "__main__":
    main()
