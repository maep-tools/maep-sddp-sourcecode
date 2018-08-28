import pickle

def historical10m():
    
    import os
    import csv
    import openpyxl
    from utils.readxlxs import xlxstocsvW10

    # Historical data wind
    alldata = []
    
    path= 'datasystem/windminutes/'
    for root,dirs,files in os.walk(path):
        xlsfiles=[ _ for _ in files if _.endswith('.xlsx') ]
        for xlsfile in xlsfiles:
            
            # import file
            importedfile = openpyxl.load_workbook(filename = os.path.join(root,xlsfile), read_only = True, keep_vba = False)
            
            tabnames = importedfile.get_sheet_names()
            xlxstocsvW10(tabnames,tabnames[0],importedfile)
            
            with open('datasystem/windminutes/'+tabnames[0]+'.csv') as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')
                singleData = [[] for x in range(2)]  
                for row in readCSV:
                    for col in range(2):
                        val = row[col]
                        try: 
                            val = float(val)
                        except ValueError:
                            pass
                        singleData[col].append(val)
            
            alldata.append(singleData)
    
    # export data            
    DataDictionary = {"historical10m":alldata}
    
    pickle.dump(DataDictionary, open( "savedata/data_historical10m.p", "wb" ) )
    
    # return DataDictionary

def format10m():
    
    import datetime
    import calendar
    
    dict_data = pickle.load( open( "savedata/data_historical10m.p", "rb" ) )
    
    winddata = dict_data['historical10m']
    
    plantyear = []
    for i in range(len(winddata)):
        plant = winddata[i][1][0]
        date = datetime.datetime.strptime (winddata[i][0][1],"%Y-%m-%d %H:%M:%S")
        plantyear.append([plant,date.year])
    
    listplants = [] ; data = []
    for i in range(len(plantyear)):
        if plantyear[i][0] not in listplants:
            
            celdasmonth = []
            for z in range(12):
                days = calendar.monthrange(plantyear[i][1],z+1)
                celdas = [[[] for x in range(24) ] for y in range(days[1]) ]
                celdasmonth.append(celdas)
                
            for z in range(len(winddata[i][0])-1):
                if '.' not in winddata[i][0][z+1]:
                    date = datetime.datetime.strptime (winddata[i][0][z+1],"%Y-%m-%d %H:%M:%S")
                    date = date + datetime.timedelta(seconds=1)
                    month = date.month; day = date.day; hour =  date.hour
                    celdasmonth[month-1][day-1][hour].append(winddata[i][1][z+1])
                    
                else:
                    val = winddata[i][0][z+1]
                    nofrag, frag = val.split('.')
                    date = datetime.datetime.strptime (nofrag,"%Y-%m-%d %H:%M:%S")
                    date = date + datetime.timedelta(seconds=1)
                    month = date.month; day = date.day; hour =  date.hour
                    celdasmonth[month-1][day-1][hour].append(winddata[i][1][z+1])
                
            data.append([plantyear[i][0],[plantyear[i][1],celdasmonth]])
            listplants.append(plantyear[i][0])
        else:
            indexP = listplants.index(plantyear[i][0])
            
            celdasmonth = []
            for z in range(12):
                days = calendar.monthrange(plantyear[i][1],z+1)
                celdas = [[[] for x in range(24) ] for y in range(days[1]) ]
                celdasmonth.append(celdas)
                
            for z in range(len(winddata[i][0])-1):
                if '.' not in winddata[i][0][z+1]:
                    date = datetime.datetime.strptime (winddata[i][0][z+1],"%Y-%m-%d %H:%M:%S")
                    date = date + datetime.timedelta(seconds=1)
                    month = date.month; day = date.day; hour =  date.hour
                    celdasmonth[month-1][day-1][hour].append(winddata[i][1][z+1])
                    
                else:
                    val = winddata[i][0][z+1]
                    nofrag, frag = val.split('.')
                    date = datetime.datetime.strptime (nofrag,"%Y-%m-%d %H:%M:%S")
                    date = date + datetime.timedelta(seconds=1)
                    month = date.month; day = date.day; hour =  date.hour
                    celdasmonth[month-1][day-1][hour].append(winddata[i][1][z+1]) 
            
            data[indexP].append([plantyear[i][1],celdasmonth])
    
    # export data            
    DataDictionary = {"windmat":data}
    
    pickle.dump(DataDictionary, open( "savedata/data_windmat.p", "wb" ) )
    