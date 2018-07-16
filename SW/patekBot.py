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

now = datetime.datetime.now()

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
                string = data[-1]
                print string
            original.close()
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
                string = data[-1]
                print string
            original.close()
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
        telegram_bot.sendMessage (chat_id, str("Hi! CircuitDigest"))
    elif command == '/time':
        telegram_bot.sendMessage(chat_id, str(now.hour)+str(":")+str(now.minute))
    elif command == '/logo':
        telegram_bot.sendPhoto (chat_id, photo = "https://i.pinimg.com/avatars/circuitdigest_1464122100_280.jpg")
    elif command == '/file':
        telegram_bot.sendDocument(chat_id, document=open('/home/pi/Aisha.py'))
    elif command == '/audio':
        telegram_bot.sendAudio(chat_id, audio=open('/home/pi/test.mp3'))
    elif command == '/meteo':
        telegram_bot.sendMessage(chat_id, getMeteo())
    elif command == '/data':
        telegram_bot.sendMessage(chat_id, getData())

telegram_bot = telepot.Bot('bot-api-key')

print (telegram_bot.getMe())

MessageLoop(telegram_bot, action).run_as_thread()

print 'Up and Running....'

while 1:
    time.sleep(10)
