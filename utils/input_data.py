def inputdata(dict_data,Param):
    
    import calendar
    import numpy as np
    import pickle
    from utils.paramvalidation import scenariosvalidation
    
    # Dictionary    
    horizon = dict_data['horizon']
    thermalData = dict_data['thermalData']
    smallData = dict_data['smallData']
    demandData = dict_data['demandData']
    blocksData = dict_data['blocksData']
    inflowData = dict_data['inflowData']
    hydroPlants = dict_data['hydroPlants']
    volData = dict_data['volData']
    thermalPlants = dict_data['thermalPlants']
    smallPlants = dict_data['smallPlants']
    numAreas = dict_data['numAreas']
    expThData = dict_data['expThData']
    expSmData = dict_data['expSmData']
    costData = dict_data['costData']
    fuelData = dict_data['fuelData']
    gatesData = dict_data['gatesData']
    biomassPlants = dict_data["biomassPlants"]
    inflowBioData = dict_data["inflowBioData"]
    biomassData = dict_data["biomassData"]
    costBData = dict_data['costBData']
    fuelBData = dict_data['fuelBData']
    
    # Daily analisys
    if Param.horizon in ['d','D','daily','Daily']:
        dict_main = pickle.load( open( "savedata/data_save_maintenance.p", "rb" ) )
        mainTpercData = dict_main['mainTpercData']
        
    ###########################################################################
            
    # Demand, series and max thermal capacity generation (MWh)    
    
    # save data
    demand = [[] for x in range(numAreas)]; yearvector = []; thermalMax = []; smallMax = []
    thermalMin = []; biomassMin = []; biomassMax = []
    
    numBlocks = len(blocksData[0]) # Number of blocks
    stages = len(demandData[0]) # number of stages
    scenarios = int((len(inflowData[0])-1)/stages) # inflow scenarios
    
    # scenarios validation
    scenariosvalidation(scenarios,Param.seriesBack)
    
    inflow_hydro = [[[] for _ in range(2) ] for _ in range(len(hydroPlants))]
    inflow_biomass = [[[] for _ in range(2) ] for _ in range(len(biomassPlants))]
    
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
        # horizon
        if Param.horizon in ['m','M','monthly','Monthly']:
            year = horizon[i].year; month = horizon[i].month
            days = calendar.monthrange(year,month); 
            aux = days[1]*24
            # if days[1] == 29: # standard
            #    aux = 28*24
            yearvector.append(aux)
        elif Param.horizon in ['d','D','daily','Daily']:
            aux = 24
            yearvector.append(24)
        
        # Demand
        for k in range (numAreas):        
            Dmon = [x*z*aux*Param.sensDem for x, z in zip(demandAux[k][0:],blocksData[0][0:])]
            demand[k].append(Dmon)
        
        # Series hydro
        for k in range(2,2+len(hydroPlants)):
            stage_inflow = inflowData[k][scenarios*i+1:scenarios*(i+1)+1]
            stage_inflow[:] = [x*(aux*3600*1e-6) for x in stage_inflow]
            if volData[7][k-2] > i+1: # initial stage for inflows
                stage_inflow[:] = [x*0 for x in stage_inflow]
            aux_inflow = np.hstack((inflow_hydro[k-2][1], stage_inflow))        
            inflow_hydro[k-2][1] = aux_inflow
        
        # Series biomass
        for k in range(2,2+len(biomassPlants)):
            stage_inflow = inflowBioData[k][scenarios*i+1:scenarios*(i+1)+1]
            if biomassData[11][k-2] > i+1: # initial stage for inflows
                stage_inflow[:] = [x*0 for x in stage_inflow]
            aux_inflow = np.hstack((inflow_biomass[k-2][1], stage_inflow))        
            inflow_biomass[k-2][1] = aux_inflow
        
        # Thermal data + unavailability
        gmax = [x * aux * (1-(z/100)) for x,z in zip(thermalData[0][0:],thermalData[9][0:])]
        gmin = [x * aux * (1-(z/100)) for x,z in zip(thermalData[6][0:],thermalData[9][0:])] 
        for k in range(len(thermalPlants)):
            if thermalData[1][k] > i+1:
                gmax[k] = gmax[k]*0
                gmin[k] = gmin[k]*0
        thermalMax.append(gmax); thermalMin.append(gmin) 
        
        # Biomass data + unavailability
        gbmax = [x * aux * (1-(z/100)) for x,z in zip(biomassData[5][0:],biomassData[15][0:])]
        gbmin = [x * aux * (1-(z/100)) for x,z in zip(biomassData[3][0:],biomassData[15][0:])] 
        for k in range(len(biomassPlants)):
            if biomassData[11][k] > i+1:
                gbmax[k] = gbmax[k]*0
                gbmin[k] = gbmin[k]*0
        biomassMax.append(gbmax); biomassMin.append(gbmin)
        
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
    
    # Biomass inflow series
    for i in range(len(biomassPlants)):
        aux_resize = np.resize(inflow_biomass[i][1], [stages,scenarios]) 
        inflow_biomass[i][0] = inflowBioData[2+i][0] 
        inflow_biomass[i][1] = aux_resize
        
    ###########################################################################

    # Expansion of thermal plants
    if len(expThData[0]) > 0:
        
        for i in range(len(expThData[0])): # loop in modificated plants
            index = thermalPlants.index(expThData[0][i])
            stagemod = expThData[1][i]
            gmaxplant = [x * expThData[2][i] * (1-(expThData[6][i]/100)) for x in yearvector[stagemod-1:]]
            
            for z in range(stagemod,stages):
                thermalMax[z][index] = gmaxplant[z-stagemod]
                thermalMin[z][index] = gmaxplant[z-stagemod]
    
    ###########################################################################

    # Maintenance
    if Param.horizon in ['d','D','daily','Daily']:
        for z in range(stages):
            for k in range(len(thermalPlants)):
                thermalMax[z][k] = thermalMax[z][k]*(1-mainTpercData[k][z])
                thermalMin[z][k] = thermalMin[z][k]*(1-mainTpercData[k][z])
                    
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
    
    # operating costs thermal
    opCost = []
    for n in range(len(thermalPlants)):
        index = costData.index(thermalData[4][n])
        opCostSingle = [x*thermalData[11][n]+thermalData[10][n] for x in fuelData[index]]
        opCost.append(opCostSingle)
    
    # operating costs biomass
    opCostBio = []
    for n in range(len(biomassPlants)):
        index = costBData.index(biomassData[10][n])
        opCostBSingle = [x*thermalData[9][n]*(1/biomassData[8][n])+biomassData[12][n] for x in fuelBData[index]]
        opCostBio.append(opCostBSingle)
        
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
    #Area biomass
    area_biomass = []
    for n in range(len(biomassPlants)): 
        area_biomass.append(biomassData[13][n])
        
    numGates = len(gatesData)
    
    ###########################################################################
    # export data - simulation data
    DataDictionary = {"thermalMax":thermalMax,"inflow_hydro":inflow_hydro,"demand":demand,
    "numBlocks":numBlocks,"area_hydro":area_hydro,"area_thermal":area_thermal,
    "opCost":opCost,"smallMax":smallMax,"area_small":area_small,"thermalMin":thermalMin,
    "numGates":numGates,"demandArea":demandArea,"inflow_biomass":inflow_biomass,
    "area_biomass":area_biomass,"biomassMin":biomassMin,"biomassMax":biomassMax,
    "opCostBio":opCostBio}
    
    pickle.dump(DataDictionary, open( "savedata/format_save.p", "wb" ) )
    
    # export - parameter's data
    DataDictionary2 = {"stagesData":stages,"scenarios":scenarios,"yearvector":yearvector}
    pickle.dump(DataDictionary2, open( "savedata/format_sim_save.p", "wb" ) )
    
    return DataDictionary, DataDictionary2
