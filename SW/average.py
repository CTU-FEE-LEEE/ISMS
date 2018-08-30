#!/usr/bin/python

import pandas as pd
import sys
import os
import time
import datetime

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
dataArchive = value['data_archive'] # archive for row data
dataUpload = value['data_upload'] # computed mean values for upload
dataCorrupted = value['data_corrupted'] # corrupted data archive
stationName = value['origin']

loop = 1
csvMeteoHeader = "Date;Wind_Dir;Wind_Speed;Gusty_wind;Precipitation;Temperature;Humidity;Atm_Pressure;Solar_Exposure;Dew_Point;Apparent_Temperature\n" #csv header
csvDataHeader = "Date;LevelMeter;Temperature1;Conductivity;Salinity;TDSKcl;Temperature2;pH;Redox;H_con" #csv header
sleepTime = 1000 # sleep time in seconds


while True:
    try:
        print("Start")
        ## Create sorted list of csv files
        listOfDataFiles = list() #empty list
        listOfMeteoFiles = list() #empty list
        listOfSpecDataFiles = list() #empty list
        files = list() #empty list
        flag = False # is computation needed
         
         
        ## METEO DATA   
        
        files = sorted(os.listdir(dataMeteo)) # list of all files and folders in directory
        
        for idx, val in enumerate(files): #goes through files
            if val.endswith("meteo.csv"): # in case of meteo.csv        
                listOfMeteoFiles.append(val) #add file to listOfFiles
        
        ## Find the newest and move the rest of meteo files
        if len(listOfMeteoFiles)>=2: # if there are more than 2 meteo files
            print("Moving meteo files...")
            for idx, file in enumerate(listOfMeteoFiles): #goes through listOfMeteoFiles except last one
                if idx < len(listOfMeteoFiles)-1:                    
                    with open(dataMeteo + file, 'r') as original: # open and read file
                        data = original.read()
                    original.close()

                    with open(dataUpload + file, 'w') as modified: # add header and save file
                        modified.write(csvMeteoHeader + data)
                        modified.flush()
                        sys.stdout.flush()
                        os.fsync(modified.fileno())
                    modified.close()
                    
                    year = file[:4]
                    month = file[4:6]                    
                    directory = dataArchive + year + "/" + month + "/"
                    
                    if not os.path.exists(directory):
                        os.makedirs(directory)                
                    os.rename(dataMeteo + file, directory + file) # move file                    
                    
            print("Moving completed")
         
         
        ##DATA  
        
        files = sorted(os.listdir(dataSource)) # list of all files and folders in directory
        
        for idx, val in enumerate(files): #goes through files
            if val.endswith("data.csv"): # in case of *data.csv        
                listOfDataFiles.append(val) #add file to listOfFiles        

        ## Find the newest and oldest and compare them. If they are from different day, compute the average of all measurement from oldest day
        if len(listOfDataFiles)>=2: # if there are more than 2 data files    
            first = listOfDataFiles[0] # get first of them
            last = listOfDataFiles[-1] # get last of them
            
            if time.mktime(datetime.datetime.strptime(last[:8], "%Y%m%d").timetuple()) > time.mktime(datetime.datetime.strptime(first[:8], "%Y%m%d").timetuple()): # if the last is older than first
                flag = True # computation needed
                print("Computing...")
                print(loop)
                loop +=1
                listOfSpecDataFiles = list() # empty list
            
                for file in listOfDataFiles: # go through data files and create list of data files measured on same day                
                    # if the day is same like the first one
                    if time.mktime(datetime.datetime.strptime(first[:8], "%Y%m%d").timetuple()) == time.mktime(datetime.datetime.strptime(file[:8], "%Y%m%d").timetuple()):
                        listOfSpecDataFiles.append(file)
                
                filename = dataUpload + first[:8]+'000000_' + stationName + '_data_mean.csv'
                
                #adding header
                with open(filename, 'w') as f:                    
                    f.write(csvDataHeader.rstrip('\r\n') + '\n')
                    f.close()
                
                for file in listOfSpecDataFiles:
                    try:
                        df=pd.read_csv(dataSource + file, sep=';', header=None) # read current csv
                        dim=df.shape # gets data file dimensions
                        rowsInd=dim[0] # maximal index of rows
                        columnsInd=dim[1] # maximal index of columns
                        values=pd.DataFrame() # empty DataFrame

                        for x in range(0,columnsInd): # for each column
                            values = values.set_value(0,x,round(df[x].mean(),3),0) #calculates mean value for all cloumns and round it by 3
                        
                        outfile = open(filename, 'a')
                        values.to_csv(filename, sep=';', header=False, index=False, mode='a') # save (add) DataFrame to csv
                        outfile.close()
                    
                    except Exception as err:
                        print (str(err))
                        print ("Corrupted data in file: " + file)
                        os.rename(dataSource + file, dataCorrupted + file) # move file
                        listOfSpecDataFiles.remove(file) # delte file from list
                        
                
                # move files to archive structure
                for file in listOfSpecDataFiles:
                    year = file[:4]
                    month = file[4:6]
                    day = file[6:8]
                    directory = dataArchive + year + "/" + month + "/" + day + "/"
                    if not os.path.exists(directory):
                        os.makedirs(directory)                
                    os.rename(dataSource + file, directory + file) # move file
                
            else:
                flag = False # computation is not needed
        else:
            flag = False # computation is not needed
        
        if flag == False:
            print ("Nothing to compute or move, waiting...")
            time.sleep(sleepTime) #long sleep, because is nothing to process
    
    except Exception as e:
        print type(e)
        print (str(e))
        time.sleep(10)