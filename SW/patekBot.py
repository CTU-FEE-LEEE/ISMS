#!/usr/bin/python

import time, datetime
import telepot
import sys
import os

from telepot.loop import MessageLoop

from mlabutils import ejson

parser = ejson.Parser()

#### Script Arguments ###############################################

if len(sys.argv) != 2:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s CONFIG_FILE\n" % (sys.argv[0], ))
    sys.exit(1)

value = parser.parse_file(sys.argv[1])
dataSource = value['data_path'] # raw data
dataMeteo = value['data_meteo'] # meteo data
stationName = value['origin']

meteoSensors = [ ['Time','unix t.s.'],
            ['Wind direction','deg'],
            ['Wind speed','m/s'],
            ['Gusty wind','m/s'],
            ['Precipitation','mm'],
            ['Temperature','C'],
            ['Humidity','%'],
            ['Atmospheric pressure','hPa'],
            ['Solar exposure','W/m2'],
            ['Dew point','C'],
            ['Apparent temperature','C'],
                                                ]
                                                
dataSensors = [ ['Time','unix t.s.'],
            ['Level meter','m'],
            ['Temperature1','C'],
            ['Conductivity','uS/cm'],
            ['Salinity','ppt'],
            ['TDS-Kcl','ppm'],
            ['Temperature2','C'],
            ['pH','-'],
            ['Redox','mV'],
                                                ]

hiMessage = "Hi,\nthis is the data logging station at Patek.\nUse /help command for overview of commands"
helpMessage = "/hi - welcome message\n/help - overview of commands\n/meteo - get latest meteo data\n/data - get latest measured data\n/meteoFile - download latest meteo file\n/dataFile - download latest data file"

def getMeteoFile():
    try:
        listOfMeteoFiles = list() #empty list

        files = sorted(os.listdir(dataMeteo)) # list of all files and folders in directory
        
        for idx, val in enumerate(files): #goes through files
            if val.endswith("meteo.csv"): # in case of meteo.csv        
                listOfMeteoFiles.append(val) #add file to listOfFiles
        
        if len(listOfMeteoFiles)>0:
            fileName = dataMeteo + listOfMeteoFiles[-1]

        else:
            fileName = "Cannot reach a file"
                

    except Exception as e:
        string = "Error: " + str(e)
        print string
        fileName = "Cannot reach a file"
        
    return fileName
    
def getDataFile():
    try:
        listOfMeteoFiles = list() #empty list

        files = sorted(os.listdir(dataSource)) # list of all files and folders in directory
        
        for idx, val in enumerate(files): #goes through files
            if val.endswith("data.csv"): # in case of meteo.csv        
                listOfMeteoFiles.append(val) #add file to listOfFiles
        
        if len(listOfMeteoFiles)>0:
            fileName = dataSource + listOfMeteoFiles[-1]

        else:
            fileName = "Cannot reach a file"
                

    except Exception as e:
        string = "Error: " + str(e)
        print string
        fileName = "Cannot reach a file"
        
    return fileName

def getMeteo():
    try:

        listOfMeteoFiles = list() #empty list

        files = sorted(os.listdir(dataMeteo)) # list of all files and folders in directory
        
        for idx, val in enumerate(files): #goes through files
            if val.endswith("meteo.csv"): # in case of meteo.csv        
                listOfMeteoFiles.append(val) #add file to listOfFiles
        
        if len(listOfMeteoFiles)>0:            
            with open(dataMeteo + listOfMeteoFiles[-1], 'r') as original: # open and read file
                data = original.readlines()
                text = data[-1]
                text = text[:-1]
            original.close()            
            
            dataList = text.split(';')
            
            string = ''
            
            for idx, val in enumerate(dataList):
                string = string + meteoSensors[idx][0] + ': ' + val + ' ' + meteoSensors[idx][1] + '\n'            
            print string
        else:
            string = "No files"
                

    except Exception as e:
        string = "Error: " + str(e)
        
    return string

def getData():
    try:

        listOfDataFiles = list() #empty list

        files = sorted(os.listdir(dataSource)) # list of all files and folders in directory        

        for idx, val in enumerate(files): #goes through files
            if val.endswith("data.csv"): # in case of meteo.csv        
                listOfDataFiles.append(val) #add file to listOfFiles      

        if len(listOfDataFiles)>0:            
            with open(dataSource + listOfDataFiles[-1], 'r') as original: # open and read file
                data = original.readlines()
                text = data[-1]
                text = text[:-1]
            original.close()
            
            dataList = text.split(';')
            
            string = ''
            
            for idx, val in enumerate(dataList):
                string = string + dataSensors[idx][0] + ': ' + val + ' ' + dataSensors[idx][1] + '\n'
            print string
        else:
            string = "No files"
                

    except Exception as e:
        string = "Error: " + str(e)
        
    return string

def action(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    print 'Received: %s' % command
    if command == '/hi':
        telegram_bot.sendMessage (chat_id, hiMessage)
    elif command == '/meteo':
        telegram_bot.sendMessage(chat_id, getMeteo())
    elif command == '/data':
        telegram_bot.sendMessage(chat_id, getData())
    elif command == '/help':
        telegram_bot.sendMessage(chat_id, helpMessage)
    elif command == '/meteoFile':
        fileName = getMeteoFile()
        if fileName is 'Cannot reach a file':
            telegram_bot.sendMessage(chat_id, fileName)
        else:
            telegram_bot.sendDocument(chat_id, document=open(fileName))
    elif command == '/dataFile':
        fileName = getDataFile()
        if fileName is 'Cannot reach a file':
            telegram_bot.sendMessage(chat_id, fileName)
        else:
            telegram_bot.sendDocument(chat_id, document=open(fileName))
        
        
# telegram_bot.sendPhoto (chat_id, photo = "https://i.pinimg.com/avatars/circuitdigest_1464122100_280.jpg")
# telegram_bot.sendDocument(chat_id, document=open('/home/pi/Aisha.py'))
# telegram_bot.sendAudio(chat_id, audio=open('/home/pi/test.mp3'))



with open('bot.key', 'r') as file: # open and read file with telegram API key
    key = file.read()
file.close()    

telegram_bot = telepot.Bot(key)

print (telegram_bot.getMe())

MessageLoop(telegram_bot, action).run_as_thread()

print 'Up and Running....'

while 1:
    time.sleep(10)
