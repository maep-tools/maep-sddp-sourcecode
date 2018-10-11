
def inputsolar(dict_data,stages):
    
    import pickle
    import numpy as np
    
    # import data
    dict_sim = pickle.load( open( "savedata/format_sim_save.p", "rb" ) )
    
    # data
    inflowSolarData = dict_data['inflowSolarData']
    numAreas = dict_data['numAreas']
    scenarios = dict_sim['scenarios']
    yearvector = dict_sim['yearvector']
    
    sPlants = [dict_data['Solar_large'], dict_data['Solar_dist']]
    sData = [dict_data['SlargeData'], dict_data['SdistData']]
    indcStage = [7, 3]
    indcArea = [8, 4]
    var_print = ['large', 'dist']
    
    stationData = []
    for i in range(len(inflowSolarData)-2):
        stationData.append(inflowSolarData[i+2][0])
    
    for typS in range(2):
        
        # save new data
        rad_solar = [[[] for _ in range(2) ] for _ in range(len(sPlants[typS]))]
        
        # Production energy limits
        numFarms = len(sPlants[typS]) # solar plants
        s_hat = [] # Limits of energy at each stage
        
        if numFarms > 0: # at least one solar power plant in the system
            for i in range(numFarms):
                # Limits of generation cosidering losses
                if typS == 0:
                    s_hat1 = [x * sData[typS][1][i] for x in yearvector[0:]]
                    for j in range(len(s_hat1)):
                        if sData[typS][indcStage[typS]][i] > j+1:
                            s_hat1[j] = 0
                    s_hat.append(s_hat1)
        
        if typS == 0:
            hat_area = [[0]*len(yearvector) for _ in range(numAreas) ] 
            for i in range(numFarms):
                areafarm = sData[typS][indcArea[typS]][i]
                hat_area[areafarm-1] = [sum(x) for x in zip(hat_area[areafarm-1], s_hat[i])]

        # solar radiation
        inflowData = []
        for n in range(len(sPlants[typS])):
            index = stationData.index(sData[typS][0][n])
            inflowData.append(inflowSolarData[2+index])
                
        totscenarios = max(inflowSolarData[1][1:])
        
        for i in range(stages):
            # Series radiation
            for k in range(len(sPlants[typS])):
                stage_solar = inflowData[k][totscenarios*i+1:totscenarios*i+1+scenarios]
                if sData[typS][indcStage[typS]][k] > i+1: # initial stage for inflows
                    stage_solar[:] = [x*0 for x in stage_solar]
                aux_solar = np.hstack((rad_solar[k][1], stage_solar))        
                rad_solar[k][1] = aux_solar
                
        # inflow series
        for i in range(len(sPlants[typS])):
            aux_resize_s = np.resize(rad_solar[i][1], [stages,scenarios]) 
            rad_solar[i][0] = inflowData[i][0] 
            rad_solar[i][1] = aux_resize_s  
    
        # export data
        DataDictionary = {"rad_solar":rad_solar}
        pickle.dump(DataDictionary, open( "savedata/solar_"+var_print[typS]+"_save.p", "wb" ) )
        
        if typS == 0:
            # export data
            DataDictionary = {"w_limit":s_hat,"hat_area":hat_area}
            pickle.dump(DataDictionary, open( "savedata/solar_large_hat.p", "wb" ) )
        
