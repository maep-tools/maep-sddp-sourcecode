from utils.readxlxs import xlxstocsv
import csv
import datetime

###############################################################################
def is_empty(any_structure):
    if any_structure:
        return False
    else:
        return True

###############################################################################
def mtxplant(substring,tabnames,horizon,importedfile,areasData,colact,colarea):
    
    xlxstocsv(tabnames,substring,importedfile)
    file_location = "temp/" + substring + ".csv"
                
    with open(file_location) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open(file_location) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        Plants = []; Data = [[] for x in range(columns-1)]  
        for row in readCSV:
            if is_empty(row) is True: break 
            tplants = row[0]; 
            Plants.append(tplants)
            for col in range(columns-1):
                val = row[col+1]
                try: 
                    val = int(row[col+1])
                except ValueError:
                    try:
                        val = float(row[col+1])
                    except ValueError:
                        pass
                Data[col].append(val)
        Plants.pop(0)
    for col in range(columns-1):
        Data[col].pop(0)
    
    state = Data[colact]
    
    for z in range(len(state)):
        if state[z] == "E":
            Data[colact][z] = 1
        elif state[z] == "NE":
            Data[colact][z] = 0
        else:
            val = datetime.datetime.strptime (state[z],"%Y-%m-%d %H:%M:%S") 
            location = horizon.index(val)
            Data[colact][z] = location+1
    
    actives = [i for i, e in enumerate(Data[colact]) if e != 0]
    Plants_act = []; Data_act = [[] for x in range(columns-1)]
    for col in range(columns-1):
        for z in range(len(actives)):
            Data_act[col].append(Data[col][actives[z]])
    for z in range(len(actives)):
            Plants_act.append(Plants[actives[z]])
    
    # Identify areas by codde
    nameAreas = Data_act[colarea]
    for z in range(len(nameAreas)):
        location = areasData[0].index(nameAreas[z])
        Data_act[colarea][z] = location+1

    return Plants_act, Data_act, actives

###############################################################################

def mtxinflow(substring,tabnames,importedfile):
    
    xlxstocsv(tabnames,substring,importedfile)
    file_location = "temp/" + substring + ".csv"
              
    with open(file_location) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open(file_location) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        Data = [[] for x in range(columns)]  
        for row in readCSV:
            if is_empty(row) is True: break 
            for col in range(2):
                val = row[col]
                try: 
                    val = int(row[col])
                except ValueError:
                    pass
                Data[col].append(val)
            for col in range(columns-2):
                val = row[col+2]
                try: 
                    val = float(row[col+2])
                except ValueError:
                    pass
                Data[col+2].append(val)
                
    return Data

def mtxincosts(substring,tabnames,importedfile):

    xlxstocsv(tabnames,substring,importedfile)
    file_location = "temp/" + substring + ".csv"
             
    with open(file_location) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break               
    with open(file_location) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        Data = [[] for x in range(columns-1)];  
        for row in readCSV:
            if is_empty(row) is True: break 
            for col in range(columns-1):
                val = row[col+1]
                try: 
                    val = float(row[col+1])
                except ValueError:
                    pass
                Data[col].append(val)
    
    fueldata = []; DataS = []
    for col in range(columns-1):
        fueldata.append(Data[col][0])
        DataS.append(Data[col].pop(0))
        
    return Data, DataS
        
###############################################################################
        
def data_file(Param, file):
    
    import openpyxl
    import csv
    import datetime
    import pickle
   
    from utils.readxlxs import xlxstocsv
    from utils.paramvalidation import areavalidation
    
    importedfile = openpyxl.load_workbook(filename = file, read_only = True, keep_vba = False)
    tabnames = importedfile.sheetnames 
    
    ###########################################################################
    substring = "Areas"
    xlxstocsv(tabnames,substring,importedfile)
    
    with open('temp/Areas.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        areasData = [[] for x in range(2)];  
        for row in readCSV:
            if is_empty(row) is True: break 
            val = row[0]
            try: 
                val = int(row[0])
            except ValueError:
                pass
            areasData[1].append(val)
            areasData[0].append(row[1])
    for col in range(2):
        areasData[col].pop(0) 
        
    numAreas = len(areasData[0]) # Number of areas in the system
    
    ###########################################################################

    substring = "Demand"
    xlxstocsv(tabnames,substring,importedfile)
                 
    with open('temp/Demand.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break                
    with open('temp/Demand.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        demandData = [[] for x in range(columns-1)];  
        for row in readCSV:
            if is_empty(row) is True: break 
            for col in range(columns-1):
                val = row[col+1]
                try: 
                    val = float(row[col+1])
                except ValueError:
                    pass
                demandData[col].append(val)
    for col in range(columns-1):
        demandData[col].pop(0) 
    
    with open('temp/Demand.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        horizon = [];  
        for row in readCSV:
            val = row [0]
            try: 
                val = datetime.datetime.strptime (row [0],"%Y-%m-%d %H:%M:%S") 
            except ValueError:
                pass
            horizon.append(val)
    horizon.pop(0) 

    ###########################################################################
    
    substring = "Thermal_config"
    xlxstocsv(tabnames,substring,importedfile)
                    
    with open('temp/Thermal_config.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open('temp/Thermal_config.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        thermalPlants = []; thermalData = [[] for x in range(columns-1)]  
        for row in readCSV:
            if is_empty(row) is True: break 
            tplants = row[0]; 
            thermalPlants.append(tplants)
            for col in range(columns-1):
                val = row[col+1]
                try: 
                    val = float(row[col+1])
                except ValueError:
                    pass
                thermalData[col].append(val)
        thermalPlants.pop(0)
    for col in range(columns-1):
        thermalData[col].pop(0)
    
    state = thermalData[1]
    for z in range(len(state)):
        if state[z] == "E":
            thermalData[1][z] = 1
        elif state[z] == "NE":
            thermalData[1][z] = 0
        else:
            val = datetime.datetime.strptime (state[z],"%Y-%m-%d %H:%M:%S") 
            location = horizon.index(val)
            thermalData[1][z] = location+1
    
    actives = [i for i, e in enumerate(thermalData[1]) if e != 0]
    thermalPlants_act = []; thermalData_act = [[] for x in range(columns-1)]
    for col in range(columns-1):
        for z in range(len(actives)):
            thermalData_act[col].append(thermalData[col][actives[z]])
    for z in range(len(actives)):
            thermalPlants_act.append(thermalPlants[actives[z]])
    
    nameAreas = thermalData_act[3]
    for z in range(len(nameAreas)):
        location = areasData[0].index(nameAreas[z])
        thermalData_act[3][z] = location+1
    
    ###########################################################################
    
    substring = "Thermal_expn"
    xlxstocsv(tabnames,substring,importedfile)
                    
    with open('temp/Thermal_expn.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open('temp/Thermal_expn.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        expThData = [[] for x in range(columns)]  
        for row in readCSV:
            if is_empty(row) is True: break 
            expThData[0].append(row[0])
            for col in range(columns-1):
                val = row[col+1]
                try: 
                    val = int(row[col+1])
                except ValueError:
                    try:
                        val = float(row[col+1])
                    except ValueError:
                        pass
                expThData[col+1].append(val)
    for col in range(columns):
        expThData[col].pop(0)
    
    state = expThData[1]
    for z in range(len(state)):
        val = datetime.datetime.strptime (state[z],"%Y-%m-%d %H:%M:%S") 
        location = horizon.index(val)
        expThData[1][z] = location+1
            
    ###########################################################################
    
    substring = "FuelCost"
    costData, costDataS = mtxincosts(substring,tabnames,importedfile)
        
    ###########################################################################
    
    substring = "RationingCosts"
    xlxstocsv(tabnames,substring,importedfile)
    
    with open('temp/RationingCosts.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        rationingData = [[] for x in range(numAreas)];  
        for row in readCSV:
            if is_empty(row) is True: break 
            for col in range(numAreas):
                val = row[col+1]
                try: 
                    val = float(row[col+1])
                except ValueError:
                    pass
                rationingData[col].append(val)
    for col in range(numAreas):
        rationingData[col].pop(0)    
    
    ###########################################################################

    substring = "Blocks"
    xlxstocsv(tabnames,substring,importedfile)
                    
    with open('temp/Blocks.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open('temp/Blocks.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        blocksData = [[] for x in range(columns-1)]  
        for row in readCSV:
            if is_empty(row) is True: break 
            for col in range(columns-1):
                val = row[col+1]
                try: 
                    val = float(row[col+1])
                except ValueError:
                    pass
                blocksData[col].append(val)
    for col in range(columns-1):
        blocksData[col].pop(0)
        
    ###########################################################################
    
    substring = "Blocks_storage"
    xlxstocsv(tabnames,substring,importedfile)
                    
    with open('temp/Blocks_storage.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open('temp/Blocks_storage.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        b_storageData = [[] for x in range(columns-1)]  
        for row in readCSV:
            if is_empty(row) is True: break 
            for col in range(columns-1):
                val = row[col+1]
                try: 
                    val = float(row[col+1])
                except ValueError:
                    pass
                b_storageData[col].append(val)
    for col in range(columns-1):
        b_storageData[col].pop(0)
        
    ###########################################################################
    
    substring = "Storage_config"
    xlxstocsv(tabnames,substring,importedfile)
                    
    with open('temp/Storage_config.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open('temp/Storage_config.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        batteries = []; battData = [[] for x in range(columns-1)]  
        for row in readCSV:
            if is_empty(row) is True: break 
            tplants = row[0]; 
            batteries.append(tplants)
            for col in range(columns-1):
                val = row[col+1]
                try: 
                    val = int(row[col+1])
                except ValueError:
                    try:
                        val = float(row[col+1])
                    except ValueError:
                        pass
                battData[col].append(val)
        batteries.pop(0)
    for col in range(columns-1):
        battData[col].pop(0)
    
    state = battData[6]
    for z in range(len(state)):
        if state[z] == "E":
            battData[6][z] = 1
        elif state[z] == "NE":
            battData[6][z] = 0
        else:
            val = datetime.datetime.strptime (state[z],"%Y-%m-%d %H:%M:%S") 
            location = horizon.index(val)
            battData[6][z] = location+1
    
    actives = [i for i, e in enumerate(battData[6]) if e != 0]
    batteries_act = []; battData_act = [[] for x in range(columns-1)]
    for col in range(columns-1):
        for z in range(len(actives)):
            battData_act[col].append(battData[col][actives[z]])
    for z in range(len(actives)):
            batteries_act.append(batteries[actives[z]])
    
    # Identify areas by codde        
    nameAreas = battData_act[9]
    for z in range(len(nameAreas)):
        location = areasData[0].index(nameAreas[z])
        battData_act[9][z] = location+1
        
    ###########################################################################    
    
    substring = "Storage_expn"
    xlxstocsv(tabnames,substring,importedfile)
                    
    with open('temp/Storage_expn.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open('temp/Storage_expn.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        expBttData = [[] for x in range(columns)]  
        for row in readCSV:
            if is_empty(row) is True: break 
            expBttData[0].append(row[0])
            for col in range(columns-1):
                val = row[col+1]
                try: 
                    val = int(row[col+1])
                except ValueError:
                    try:
                        val = float(row[col+1])
                    except ValueError:
                        pass
                expBttData[col+1].append(val)
    for col in range(columns):
        expBttData[col].pop(0)
    
    state = expBttData[1]
    for z in range(len(state)):
        val = datetime.datetime.strptime (state[z],"%Y-%m-%d %H:%M:%S") 
        location = horizon.index(val)
        expBttData[1][z] = location+1
            
    ###########################################################################
    
    substring = "Hydro_config"
    xlxstocsv(tabnames,substring,importedfile)
                    
    with open('temp/Hydro_config.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open('temp/Hydro_config.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        hydroPlants = []; volData = [[] for x in range(columns-1)]  
        for row in readCSV:
            if is_empty(row) is True: break 
            tplants = row[0]; 
            hydroPlants.append(tplants)
            for col in range(columns-1):
                val = row[col+1]
                try: 
                    val = int(row[col+1])
                except ValueError:
                    try:
                        val = float(row[col+1])
                    except ValueError:
                        pass
                volData[col].append(val)
        hydroPlants.pop(0)
    for col in range(columns-1):
        volData[col].pop(0)
    
    state = volData[6]
    for z in range(len(state)):
        if state[z] == "E":
            volData[6][z] = 1
        elif state[z] == "NE":
            volData[6][z] = 0
        else:
            val = datetime.datetime.strptime (state[z],"%Y-%m-%d %H:%M:%S") 
            location = horizon.index(val)
            volData[6][z] = location+1
    
    actives = [i for i, e in enumerate(volData[6]) if e != 0]
    hydroPlants_act = []; volData_act = [[] for x in range(columns-1)]
    for col in range(columns-1):
        for z in range(len(actives)):
            volData_act[col].append(volData[col][actives[z]])
    hPlantsReser = []
    for z in range(len(actives)):
        hydroPlants_act.append(hydroPlants[actives[z]])
        if (volData[2][actives[z]] > 0 and volData[3][actives[z]] > 0):
            hPlantsReser.append(1)
        else:
            hPlantsReser.append(0)
    
    # Identify areas by codde
    nameAreas = volData_act[11]
    for z in range(len(nameAreas)):
        try:
            location = areasData[0].index(nameAreas[z])
            volData_act[11][z] = location+1
        except ValueError:
            areavalidation(nameAreas[z],substring)
    
    # Initial conditions of each reservoir
    for z in range(len(volData_act[0])):
        volIni = volData_act[0][z]*volData_act[2][z]
        volData_act[0][z] = volIni
        
    ###########################################################################
    
    substring = "Hydro_expn"
    xlxstocsv(tabnames,substring,importedfile)
                    
    with open('temp/Hydro_expn.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open('temp/Hydro_expn.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        expData = [[] for x in range(columns)]  
        for row in readCSV:
            if is_empty(row) is True: break 
            expData[0].append(row[0])
            for col in range(columns-1):
                val = row[col+1]
                try: 
                    val = int(row[col+1])
                except ValueError:
                    try:
                        val = float(row[col+1])
                    except ValueError:
                        pass
                expData[col+1].append(val)
    for col in range(columns):
        expData[col].pop(0)
    
    state = expData[4]
    for z in range(len(state)):
        val = datetime.datetime.strptime (state[z],"%Y-%m-%d %H:%M:%S") 
        location = horizon.index(val)
        expData[4][z] = location+1
    
    ###########################################################################
    
    substring = "Inflow"
    xlxstocsv(tabnames,substring,importedfile)
                    
    with open('temp/Inflow.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open('temp/Inflow.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        inflowData = [[] for x in range(columns)]  
        for row in readCSV:
            if is_empty(row) is True: break 
            for col in range(2):
                val = row[col]
                try: 
                    val = int(row[col])
                except ValueError:
                    pass
                inflowData[col].append(val)
            for col in range(columns-2):
                val = row[col+2]
                try: 
                    val = float(row[col+2])
                except ValueError:
                    pass
                inflowData[col+2].append(val)
    
    inflowData_act = []
    inflowData_act.append(inflowData[0])
    inflowData_act.append(inflowData[1])
    for z in range(len(actives)):
        inflowData_act.append(inflowData[actives[z]+2])
        
    ###########################################################################
    
    # wind power plants
    substring = "Wind_config"
    windPlants,windData,activesW = mtxplant(substring,tabnames,horizon,
                                                   importedfile,areasData,6,8)
    # Wind inflows
    inflowWindData = []
    inflowWindData.append(inflowData[0])
    inflowWindData.append(inflowData[1])
    
    substring = "InflowWind"
    mtx_Data = mtxinflow(substring,tabnames,importedfile)
    
    for z in range(len(activesW)):
        inflowWindData.append(mtx_Data[activesW[z]+2])
        
    # Wind speed indices
    indicesData = []
    substring = "SpeedIndices"
    mtx_DataIn = mtxinflow(substring,tabnames,importedfile)
    
    for z in range(len(activesW)):
        indicesData.append(mtx_DataIn[activesW[z]+2])
        
    # wind expansion
    substring = "Wind_expn"
    xlxstocsv(tabnames,substring,importedfile)
                    
    with open('temp/Wind_expn.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open('temp/Wind_expn.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        expWindData = [[] for x in range(columns)]  
        for row in readCSV:
            if is_empty(row) is True: break 
            expWindData[0].append(row[0])
            for col in range(columns-1):
                val = row[col+1]
                try: 
                    val = int(row[col+1])
                except ValueError:
                    try:
                        val = float(row[col+1])
                    except ValueError:
                        pass
                expWindData[col+1].append(val)
    for col in range(columns):
        expWindData[col].pop(0)
    
    state = expWindData[1]
    for z in range(len(state)):
        val = datetime.datetime.strptime (state[z],"%Y-%m-%d %H:%M:%S") 
        location = horizon.index(val)
        expWindData[1][z] = location+1
        
    ###########################################################################
    
    # Data wind model 2
    if Param.wind_model2 is True:
        
        substring = "Wind_M2_config"
        xlxstocsv(tabnames,substring,importedfile)
                        
        with open('temp/Wind_M2_config.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV: columns = len(row); break
        with open('temp/Wind_M2_config.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            windRPlants = []; windRData = [[] for x in range(columns-1)]  
            for row in readCSV:
                if is_empty(row) is True: break 
                tplants = row[0]; 
                windRPlants.append(tplants)
                for col in range(columns-1):
                    val = row[col+1]
                    try: 
                        val = int(row[col+1])
                    except ValueError:
                        try:
                            val = float(row[col+1])
                        except ValueError:
                            pass
                    windRData[col].append(val)
            windRPlants.pop(0)
        for col in range(columns-1):
            windRData[col].pop(0)
        
        state = windRData[11]
        for z in range(len(state)):
            if state[z] == "E":
                windRData[11][z] = 1
            elif state[z] == "NE":
                windRData[11][z] = 0
            else:
                val = datetime.datetime.strptime (state[z],"%Y-%m-%d %H:%M:%S") 
                location = horizon.index(val)
                windRData[11][z] = location+1
        
        actives = [i for i, e in enumerate(windRData[11]) if e != 0]
        windRPlants_act = []; windRData_act = [[] for x in range(columns-1)]
        for col in range(columns-1):
            for z in range(len(actives)):
                windRData_act[col].append(windRData[col][actives[z]])
        for z in range(len(actives)):
                windRPlants_act.append(windRPlants[actives[z]])
        
        # Identify areas by codde
        nameAreas = windRData_act[12]
        for z in range(len(nameAreas)):
            try:
                location = areasData[0].index(nameAreas[z])
                windRData_act[12][z] = location+1
            except ValueError:
                areavalidation(nameAreas[z],substring)
                
        # inflow model 2
        substring = "InflowWind_M2"
        xlxstocsv(tabnames,substring,importedfile)
                        
        with open('temp/InflowWind_M2.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV: columns = len(row); break
        with open('temp/InflowWind_M2.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            inflowRealData = [[] for x in range(columns)]  
            for row in readCSV:
                for col in range(2):
                    val = row[col]
                    try: 
                        val = int(row[col])
                    except ValueError:
                        pass
                    inflowRealData[col].append(val)
                for col in range(columns-2):
                    val = row[col+2]
                    try: 
                        val = float(row[col+2])
                    except ValueError:
                        pass
                    inflowRealData[col+2].append(val)
        
        # inflows for real wind plants
        inflowRealData_act = []
        inflowRealData_act.append(inflowData[0])
        inflowRealData_act.append(inflowData[1])
        for z in range(len(actives)):
            inflowRealData_act.append(inflowRealData[actives[z]+2])
        
        # indices model 2
        substring = "SpeedIndices_M2"
        xlxstocsv(tabnames,substring,importedfile)
                        
        with open('temp/SpeedIndices_M2.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV: columns = len(row); break
        with open('temp/SpeedIndices_M2.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            indicesRData = [[] for x in range(columns)]  
            for row in readCSV:
                if is_empty(row) is True: break 
                for col in range(2):
                    val = row[col]
                    try: 
                        val = int(row[col])
                    except ValueError:
                        pass
                    indicesRData[col].append(val)
                for col in range(columns-2):
                    val = row[col+2]
                    try: 
                        val = float(row[col+2])
                    except ValueError:
                        pass
                    indicesRData[col+2].append(val)
    
        for col in range(columns):
            indicesRData[col].pop(0)
            
        indicesRData_act = []
        for z in range(len(actives)):
            indicesRData_act.append(indicesRData[actives[z]+2])
        
        # power curve model2
        substring = "WPowCurve_M2"
        xlxstocsv(tabnames,substring,importedfile)
        
        with open('temp/WPowCurve_M2.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            powerData = [[] for x in range(len(windRPlants)*3)]               
            for row in readCSV:
                for col in range(len(windRPlants)*3):
                    val = row[col]
                    try: 
                        val = float(row[col])
                    except ValueError:
                        pass
                    powerData[col].append(val)
        for col in range(len(windRPlants)*3):
            powerData[col].pop(0)            
        ctData = [[] for x in range(len(windRPlants))]
        for z in range(len(windRPlants)):
            resl = int(1+((windRData[3][z]-windRData[2][z])/windRData[4][z]))
            pw = powerData[3*z][:resl]
            ct = powerData[3*z+1][:resl]
            tpr = powerData[3*z+2][:windRData[14][z]] 
            ctData[z]=[pw,ct,tpr]
        
        ctData_act = []
        for z in range(len(actives)):
            ctData_act.append(ctData[actives[z]])
            
    ###########################################################################
    
    substring = "Lines"
    xlxstocsv(tabnames,substring,importedfile)
    
    if numAreas != 1:
        with open('temp/Lines.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV: columns = len(row); break
        with open('temp/Lines.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            linesData = [] 
            for row in readCSV:
                if is_empty(row) is True: break 
                rowval=[]
                rowval.append(row[0]); rowval.append(row[1])
                for col in range(columns-2):
                    try:
                        val = float(row[col+2])
                    except ValueError:
                        pass    
                    rowval.append(val)
                linesData.append(rowval)
        linesData.pop(0)
        
        # Identify areas by code
        for z in range(len(linesData)):
            location1 = areasData[0].index(linesData[z][0])
            location2 = areasData[0].index(linesData[z][1])
            linesData[z][0] = location1+1; linesData[z][1] = location2+1
        
    else:
        with open('temp/Lines.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV: columns = len(row); break
        with open('temp/Lines.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            linesData = [] 
            for row in readCSV:
                rowval=[]
                for col in range(columns):
                    rowval.append(0)
                linesData.append(rowval)
        linesData.pop(0)    
    
    ###########################################################################
    
    substring = "Lines_expn"
    xlxstocsv(tabnames,substring,importedfile)
                    
    with open('temp/Lines_expn.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open('temp/Lines_expn.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        expLinesData = []  

        for row in readCSV:
            if is_empty(row) is True: break 
            vecdata = [row[0],row[1]]
            for col in range(columns-2):
                
                val = row[col+2]
                try: 
                    val = int(val)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                vecdata.append(val)
            expLinesData.append(vecdata)
    
    expLinesData.pop(0) 
    for z in range(len(expLinesData)):
        val = datetime.datetime.strptime (expLinesData[z][2],"%Y-%m-%d %H:%M:%S") 
        location = horizon.index(val)
        expLinesData[z][2] = location+1

        location1 = areasData[0].index(expLinesData[z][0])
        location2 = areasData[0].index(expLinesData[z][1])
        expLinesData[z][0] = location1+1; expLinesData[z][1] = location2+1
    
    ###########################################################################
    
    substring = "FlowGates"
    xlxstocsv(tabnames,substring,importedfile)
                    
    with open('temp/FlowGates.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open('temp/FlowGates.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        gatesData = []  

        for row in readCSV:
            if is_empty(row) is True: break 
            vecdata = [row[1],row[2],row[3],row[4]]
            for col in range(12):
                
                val = row[col+5]
                try: 
                    valarea = 1+areasData[0].index(val)
                    val = int(valarea)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                vecdata.append(val)
            gatesData.append(vecdata)
    
    if Param.flow_gates is True:
        gatesData.pop(0) 
        for z in range(len(gatesData)):
            
            val = datetime.datetime.strptime (gatesData[z][2],"%Y-%m-%d %H:%M:%S") 
            valfin = datetime.datetime.strptime (gatesData[z][3],"%Y-%m-%d %H:%M:%S")
    
            location = horizon.index(val)
            gatesData[z][2] = location+1
            locationfin = horizon.index(valfin)
            gatesData[z][3] = locationfin+1
    
            gatesData[z][0] = int(gatesData[z][0])
            gatesData[z][1] = float(gatesData[z][1])
        
    ###########################################################################
    
    # Small plants
    substring = "Small_config"
    smallPlants_act,smallData_act,smactives = mtxplant(substring,tabnames,horizon,importedfile,
                                       areasData,1,3)
                
    substring = "Small_expn"
    xlxstocsv(tabnames,substring,importedfile)
                    
    with open('temp/Small_expn.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break
    with open('temp/Small_expn.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        expSmData = [[] for x in range(columns)]  
        for row in readCSV:
            if is_empty(row) is True: break 
            expSmData[0].append(row[0])
            for col in range(columns-1):
                val = row[col+1]
                try: 
                    val = int(row[col+1])
                except ValueError:
                    try:
                        val = float(row[col+1])
                    except ValueError:
                        pass
                expSmData[col+1].append(val)
    for col in range(columns):
        expSmData[col].pop(0)
    
    state = expSmData[1]
    for z in range(len(state)):
        val = datetime.datetime.strptime (state[z],"%Y-%m-%d %H:%M:%S") 
        location = horizon.index(val)
        expSmData[1][z] = location+1
    
    ###########################################################################
    
    substring = "EmissionsCosts"
    xlxstocsv(tabnames,substring,importedfile)
    
    with open('temp/EmissionsCosts.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break 
    with open('temp/EmissionsCosts.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        emissionsData = [[] for x in range(columns-1)];  
        for row in readCSV:
            if is_empty(row) is True: break 
            for col in range(columns-1):
                val = row[col+1]
                try: 
                    val = float(row[col+1])
                except ValueError:
                    pass
                emissionsData[col].append(val)
    for col in range(columns-1):
        emissionsData[col].pop(0) 
    
    ###########################################################################
    
    # Big solar
    substring = "SolarL_config"
    SB_act,SBData,SBactives = mtxplant(substring,tabnames,horizon,importedfile,
                                       areasData,7,8)
    # Distributed solar
    substring = "SolarD_config"
    SD_act,SDData,SDactives = mtxplant(substring,tabnames,horizon,importedfile,
                                       areasData,3,4)
    # Solar inflows
    substring = "InflowSolar"
    inflowSolarData = mtxinflow(substring,tabnames,importedfile)
    
    # Solar temperature
    substring = "TemperatureCell"
    TemperatureCell = mtxinflow(substring,tabnames,importedfile)
    
    # Solar speed indices
    substring = "RadiationIndices"
    indicesRadData = mtxinflow(substring,tabnames,importedfile)
    
    ###########################################################################
    
    # Big solar
    substring = "Biomass_config"
    BM_act,BMData,BMactives = mtxplant(substring,tabnames,horizon,importedfile,
                                       areasData,11,13)
    # Solar inflows
    substring = "Mass_Inflow"
    inflowBioData = mtxinflow(substring,tabnames,importedfile)
    
    substring = "MassCost"
    costBData, costBDataS = mtxincosts(substring,tabnames,importedfile)
    
    ###########################################################################
    
    # Daily analisys
    if Param.horizon in ['d','D','daily','Daily']:
        
        substring = "T_Maintenance"
        tmaintData, tmaintDataS = mtxincosts(substring,tabnames,importedfile)
        
        substring = "H_Maintenance"
        hmaintData, hmaintDataS = mtxincosts(substring,tabnames,importedfile)
        
        # export data            
        DataDictionary3 = {"mainHpercData":hmaintData,"mainHData":hmaintDataS,
        "mainTpercData":tmaintData,"mainTData":tmaintDataS}
        
        pickle.dump(DataDictionary3, open( "savedata/data_save_maintenance.p", "wb" ) )
    
    ###########################################################################
    
    # export data   
    if Param.wind_model2 is True:
        DataDictionary = { "inflowData":inflowData_act,"inflowWindData":inflowWindData,
        "blocksData":blocksData,"horizon":horizon,"demandData":demandData, 
        "thermalData":thermalData_act,"thermalPlants":thermalPlants_act,"expThData":expThData,
        "hydroPlants":hydroPlants_act,"volData":volData_act,"windPlants":windPlants,
        "windData":windData,"battData":battData_act,"batteries":batteries_act,"linesData":linesData,
        "numAreas":numAreas,"areasData":areasData,"expData":expData,"expLines":expLinesData,
        "hydroReservoir":hPlantsReser,"expWindData":expWindData,"expBttData":expBttData,
        "smallData":smallData_act,"smallPlants":smallPlants_act,"expSmData":expSmData,
        "indicesData":indicesData, "costData":costDataS, "fuelData":costData,
        "windRPlants":windRPlants_act,"windRData":windRData_act,"inflowRealData":inflowRealData_act,
        "indicesRData":indicesRData_act,"ctData_act":ctData_act,"gatesData":gatesData, 
        "costData":costDataS, "fuelData":costData,"costBData":costBDataS, "fuelBData":costBData}
    else:
        DataDictionary = { "inflowData":inflowData_act,"inflowWindData":inflowWindData,
        "blocksData":blocksData,"horizon":horizon,"demandData":demandData, 
        "thermalData":thermalData_act,"thermalPlants":thermalPlants_act,"expThData":expThData,
        "hydroPlants":hydroPlants_act,"volData":volData_act,"windPlants":windPlants,
        "windData":windData,"battData":battData_act,"batteries":batteries_act,"linesData":linesData,
        "numAreas":numAreas,"areasData":areasData,"expData":expData,"expLines":expLinesData,
        "hydroReservoir":hPlantsReser,"expWindData":expWindData,"expBttData":expBttData,
        "smallData":smallData_act,"smallPlants":smallPlants_act,"expSmData":expSmData,
        "indicesData":indicesData, "costData":costDataS, "fuelData":costData,"gatesData":gatesData,
        "Solar_large":SB_act,"SlargeData":SBData,"Solar_dist":SD_act,"SdistData":SDData,
        "inflowSolarData":inflowSolarData,"indicesRad":indicesRadData,"TemperatureCell":TemperatureCell,
        "biomassPlants":BM_act,"biomassData":BMData,"inflowBioData":inflowBioData, 
        "costData":costDataS, "fuelData":costData,"costBData":costBDataS, "fuelBData":costBData}
        
    pickle.dump(DataDictionary, open( "savedata/data_save.p", "wb" ) )
    
    # export data            
    DataDictionary2 = {"blocksData":blocksData,"rationingData":rationingData,
    "thermalPlants":thermalPlants_act,"hydroPlants":hydroPlants_act,"numAreas":numAreas,
    "volData":volData_act,"windPlants":windPlants,"battData":battData_act,
    "batteries":batteries_act,"linesData":linesData,"hydroReservoir":hPlantsReser,
    "smallPlants":smallPlants_act,"emissionsData":emissionsData,"thermalData":thermalData_act,
    "smallData":smallData_act,"windData":windData,"b_storageData":b_storageData,
    "biomassPlants":BM_act,"biomassData":BMData}
    
    pickle.dump(DataDictionary2, open( "savedata/data_save_iter.p", "wb" ) )
      
