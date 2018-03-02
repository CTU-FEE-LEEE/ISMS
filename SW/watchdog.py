#!/usr/bin/env python

# sudo modprobe bcm_wdt - raspberry
# http://raspberrypi.werquin.com/post/44890705367/a-hardware-watchdog-to-monitor-a-deamon-running

# 
import thread
import time
import os
import signal
import psutil
from watchdogdev import *
import sys

from mlabutils import ejson
parser = ejson.Parser()

#### Script Arguments ###############################################

if len(sys.argv) != 2:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s CONFIG_FILE\n" % (sys.argv[0], ))
    sys.exit(1)

value = parser.parse_file(sys.argv[1])
path = value['data_path'] # raw data  /home/pi/Documents/Vrty/watchdog/test
sleepTime = value['WD_interval'] # sleep interval for soft. WD
errCnt = value['error_counter'] # error counter for soft. WD

#### Declaration ###############################################

wd = watchdog('/dev/watchdog')
g_interrupt = 0
g_HWWDSleep = 1

#### Function definition ###############################################

def hwwd():
    while g_interrupt == 0:
        """
        Hardware watchdog
        """
        print "WD on, left:",wd.get_time_left()
        wd.keep_alive()
        time.sleep(g_HWWDSleep)
    # HWWD Off    
    wd.magic_close()
    print "HW-WD off"

def conTest(hostname = "google.com"):    
    """
    Connection test - ping to server
    google.com by default
    """       
    response = os.system("ping -c 1 -w 4 " + hostname + " > /dev/null 2>&1")
    return response

def getSize(start_path = '.'):
    """
    Return folder size
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def getMemUsage():
    """
    Return precentage usage of memory
    """
    info = psutil.virtual_memory()
    return info.percent

def writeLog(report):
    """
    Write a report line to log file with current time
    """
    try:
        with open("log.txt", "a", 0) as f:
            f.write("%d,%s\n" % (time.time(), str(report)))
            f.flush()
        f.close()
    except:
        print("Cannot write to log file (log.txt)")
    
def reboot(msg = "default"):
    """
    Soft reboot of the system
    """
    # stop WH WD
    g_interrupt = 1
    # wait for HWWD process
    time.sleep(g_HWWDSleep+1)    

    writeLog("Rebooting: " + msg)
    os.system('reboot')

#### Main Procedure ###############################################

def main():
    global g_interrupt
    global sleepTime
    global path
    global errCnt
    folderSize = -1

    # error coutners
    errCntConn = 0
    errCntFolder = 0

    # Handler for key interrupt
    def handler(signum, frame):
        global g_interrupt
        g_interrupt = 1        
        
    try:
        thread.start_new_thread(hwwd,())        
    except:
        print "Error: unable to start thread"
        wd.magic_close()
         
    signal.signal(signal.SIGINT, handler)
    writeLog("Starting watchdog daemon")

    while g_interrupt == 0:
        ## connection test
        if conTest("space.astro.cz") == 0:
            print "Connection test: PASS"
            errCntConn  = 0
        else:
            errCntConn += 1
            msg = "Connection test: FAIL. Connection error counter:" + str(errCntConn)
            writeLog(msg)
            print msg

        if errCntConn >= errCnt:
            reboot("Connection test error - exceed boundaries")
            break

        ## Folder size test
        if folderSize != getSize(path):
            print "Folder size test: PASS"
            errCntFolder = 0
            folderSize = getSize(path)
        else:
            errCntFolder += 1
            msg = "Folder size test: FAIL. Folder size error counter: " + str(errCntFolder)
            writeLog(msg)
            print msg

        if errCntFolder >= errCnt:
            reboot("Folder size test error - exceed boundaries")
            break

        ## Memory usage test
        if getMemUsage() < 95:
            print "Memory usage test: PASS"            
        else:            
            msg = "Memory usage test: FAIL. Memory usage:" + str(getMemUsage()) + "%"
            print msg
            reboot("Memory usage test error - " + str(getMemUsage()) + "% used")
                
        #sleep section
        print "--------------------------"        
        for i in range(2*sleepTime):
            if g_interrupt == 1:                
                break
            time.sleep(0.5)

    print "\nEnding..."
    time.sleep(g_HWWDSleep+1)
    #wd.magic_close()
    writeLog("Closing watchdog daemon")
    print "HW-WD off"
    print "Done"



if __name__ == "__main__":
    main()
