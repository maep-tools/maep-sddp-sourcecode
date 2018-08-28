def inputdata(dictionary,sensDem):
    
    import calendar
    import numpy as np
    import pickle
    
    # Dictionary    
    horizon = dictionary['horizon']
    thermalData = dictionary['thermalData']
    smallData = dictionary['smallData']
    demandData = dictionary['demandData']
    blocksData = dictionary['blocksData']
    inflowData = dictionary['inflowData']
    hydroPlants = dictionary['hydroPlants']
    volData = dictionary['volData']
    thermalPlants = dictionary['thermalPlants']
    smallPlants = dictionary['smallPlants']
    numAreas = dictionary['numAreas']
    expThData = dictionary['expThData']
    expSmData = dictionary['expSmData']
    costData = dictionary['costData']
    fuelData = dictionary['fuelData']
    gatesData = dictionary['gatesData']
    
    ###########################################################################
            
    # Demand, series and max thermal capacity generation (MWh)    
    
    # save data
    demand = [[] for x in range(numAreas)]; yearvector = []; thermalMax = []; smallMax = []
    thermalMin = []
    
    numBlocks = len(blocksData[0]) # Number of blocks
    stages = len(demandData[0]) # number of stages
    scenarios = int((len(inflowData[0])-1)/stages) # inflow scenarios
    
    inflow_hydro = [[[] for _ in range(2) ] for _ in range(len(hydroPlants))]
    
    # areas with demand
    demandArea = []
    for z in range (numAreas):
        if demandData[z+1][0] > 0:
            demandArea.append(z+1)
            
    # demand
    for i in range(stages):
        
        demandAux = []
        for z in range (numAreas):
            demandAux_area = []
            for k in range(numBlocks):
                demandAux_area.append(demandData[0][i]*demandData[z+1][i]*blocksData[z+1][k])
            demandAux.append(demandAux_area)
        year = horizon[i].year; month = horizon[i].month
        days = calendar.monthrange(year,month); 
        aux = days[1]*24
        if days[1] == 29:
            aux = 28*24
        yearvector.append(aux)
        # Demand
        for k in range (numAreas):        
            Dmon = [x*z*aux*sensDem for x, z in zip(demandAux[k][0:],blocksData[0][0:])]
            demand[k].append(Dmon)
        # Series
        for k in range(2,2+len(hydroPlants)):
            stage_inflow = inflowData[k][scenarios*i+1:scenarios*(i+1)+1]
            stage_inflow[:] = [x*(aux*3600*1e-6) for x in stage_inflow]
            if volData[7][k-2] > i+1: # initial stage for inflows
                stage_inflow[:] = [x*0 for x in stage_inflow]
            aux_inflow = np.hstack((inflow_hydro[k-2][1], stage_inflow))        
            inflow_hydro[k-2][1] = aux_inflow
        
        # Thermal data + unavailability
        gmax = [x * aux * (1-(z/100)) for x,z in zip(thermalData[0][0:],thermalData[9][0:])]
        gmin = [x * aux * (1-(z/100)) for x,z in zip(thermalData[6][0:],thermalData[9][0:])] 
        for k in range(len(thermalPlants)):
            if thermalData[1][k] > i+1:
                gmax[k] = gmax[k]*0
                gmin[k] = gmin[k]*0
        thermalMax.append(gmax); thermalMin.append(gmin) 
        
        # Small plants + unavailability
        gmaxSmall = [x * aux * (1-(z/100)) for x,z in zip(smallData[0][0:],smallData[7][0:])] 
        for k in range(len(smallPlants)):
            if smallData[1][k] > i+1:
                gmaxSmall[k] = gmaxSmall[k]*0
        smallMax.append(gmaxSmall) 
        
    # Hydro inflow series
    for i in range(len(hydroPlants)):
        aux_resize = np.resize(inflow_hydro[i][1], [stages,scenarios]) 
        inflow_hydro[i][0] = inflowData[2+i][0] 
        inflow_hydro[i][1] = aux_resize
    
    ###########################################################################

    # Expansion of thermal plants
    if len(expThData[0]) > 0:
        
        for i in range(len(expThData[0])): # loop in modificated plants
            index = thermalPlants.index(expThData[0][i])
            stagemod = expThData[1][i]
            gmaxplant = [x * expThData[2][i] * (1-(expThData[6][i]/100)) for x in yearvector[stagemod-1:]]
            
            for z in range(stagemod,stages+1):
                thermalMax[z-1][index] = gmaxplant[z-stagemod]
        
    ###########################################################################
    
    # Expansion of small plants
    if len(expSmData[0]) > 0:
        
        for i in range(len(expSmData[0])): # loop in modificated plants
            index = smallPlants.index(expSmData[0][i])
            stagemod = expSmData[1][i]
            gmaxSmplant = [x * expSmData[2][i] * (1-(expSmData[4][i]/100)) for x in yearvector[stagemod-1:]]
            
            for z in range(stagemod,stages+1):
                smallMax[z-1][index] = gmaxSmplant[z-stagemod]
        
    ###########################################################################
    
    # operating costs
    opCost = []
    for n in range(len(thermalPlants)):
        index = costData.index(thermalData[4][n])
        opCostSingle = [x*thermalData[11][n]+thermalData[10][n] for x in fuelData[index]]
        opCost.append(opCostSingle)
    
    ###########################################################################
    
    # Area thermal       
    area_thermal = []
    for n in range(len(thermalPlants)): 
        area_thermal.append(thermalData[3][n])
    # Area small plants
    area_small = []
    for n in range(len(smallPlants)): 
        area_small.append(smallData[3][n])
    #Area hydro
    area_hydro = []
    for n in range(len(hydroPlants)): 
        area_hydro.append(volData[11][n])
    
    numGates = len(gatesData)
    
    ###########################################################################
    # export data - simulation data
    DataDictionary = {"thermalMax":thermalMax,"inflow_hydro":inflow_hydro,"demand":demand,
    "numBlocks":numBlocks,"area_hydro":area_hydro,"area_thermal":area_thermal,
    "opCost":opCost,"smallMax":smallMax,"area_small":area_small,"thermalMin":thermalMin,
    "numGates":numGates,"demandArea":demandArea}
    
    pickle.dump(DataDictionary, open( "savedata/format_save.p", "wb" ) )
    
    # export - parameter's data
    DataDictionary2 = {"stagesData":stages,"scenarios":scenarios,"yearvector":yearvector}
    pickle.dump(DataDictionary2, open( "savedata/format_sim_save.p", "wb" ) )
    
    return DataDictionary, DataDictionary2