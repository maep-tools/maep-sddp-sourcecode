import pickle
import numpy as np

###############################################################################

def power(RnwArea,power_area,blocksData,scenarios,stages,yearvector):
    
    # Areas - energy 
    power_area_energy = []
    for area in range(len(RnwArea)):
        ene_area = power_area[area]
        
        power_temp = [[[[] for x in range(len(blocksData[0])) ] for y in range(scenarios)] for z in range(stages)]
        
        for n in range(stages): 
            for k in range(scenarios): 
                for j in range(len(blocksData[0])): 
                    sum_p = 0
                    for i in range(len(ene_area)):
                        sum_p += ene_area[i][n][k][j]
                        
                    energy_area = sum_p * yearvector[n]*blocksData[0][j]
                    power_temp[n][k][j]= energy_area
                    
        # save data areas
        power_area_energy.append(power_temp)
    
    return power_area_energy 

###############################################################################
    
def inputAvrWind(dict_data,Param):    
    
    dict_wind = pickle.load( open( "savedata/wind_save0.p", "rb" ) )
    dict_sim = pickle.load( open( "savedata/format_sim_save.p", "rb" ) )
    
    windPlants = dict_data['windPlants']
    indicesData = dict_data['indicesData']
    blocksData = dict_data['blocksData']
    scenarios = Param.seriesForw
    speed_wind = dict_wind['speed_wind']
    windData = dict_data['windData']
    numAreas = dict_data['numAreas']
    yearvector = dict_sim['yearvector']

    # save data
    power_area = [] # pmax = [0]*numAreas
    RnwArea = []
    
    for col in range(len(windPlants)):
        indicesData[col].pop(0)
        
    for area in range(numAreas):
        
        # Set of plants for each area
        windP = 0; speed_wind_temp = []; intensities=[]; index=[]; 
        for i in range(len(windPlants)):
            if windData[8][i] == area+1:
                windP += 1
                # pmax[area] = pmax[area] + windData[0][i]
                speed_wind_temp.append(speed_wind[i])
                index.append(i)
                
                # matrix of intensities must be ordered to correspond with month
                intensity = np.resize(indicesData[i], [12,len(blocksData[0])])
                aux = 0; aux2 = 0; intensityPlant=[]
                for n in range(Param.stages):
                    intensityPlant.append(intensity[n-aux2])
                    if ((n+1)/12)-1 == aux:
                        aux += 1; aux2 += 12
                
                intensities.append(intensityPlant)
        
        if windP != 0:
            # save areas with renewables
            
            RnwArea.append(area+1)
            
            # Inflow by blocks with short term variability
            power_wind_var = [[[[] for x in range(scenarios) ] for y in range(Param.stages)] for z in range(windP)]
            for i in range(windP):
                
                # number of turbines
                idx = index[i]
                numTbn = windData[0][idx] / ( (3.1416/8)*windData[2][idx]*windData[13][idx]*(windData[4][idx]**2)*(windData[5][idx]**3) / 1e6)
                
                # wind power
                 
                o_idx = (3.1416/8)*windData[2][idx]*windData[3][idx]*(windData[4][idx]**2)*numTbn
                p_nom = (windData[5][idx]**3) * o_idx #  /1e6
                p_max = (windData[12][idx]**3) * o_idx #/1e6
                p_min = (windData[11][idx]**3) * o_idx #/1e6
                
                for n in range(Param.stages): 
                    scenario_inflow = speed_wind_temp[i][1][n]
                    for k in range(scenarios): 
                        speed_sc = []
                        for j in range(len(blocksData[0])): 
                            
                            if scenario_inflow[k] > 0:
                                
                                mu = scenario_inflow[k]*intensities[i][n][j]
                                avg_val = (mu**3 )*o_idx * windData[1][idx]
                                    
                                if avg_val > p_max or avg_val <= p_min:
                                    speed_sc.append(0)
                                elif avg_val > p_nom and avg_val <= p_max:
                                    speed_sc.append(p_nom)
                                elif avg_val > p_min and avg_val <= p_nom:
                                    speed_sc.append(avg_val)
                                
                            else:
                                # Plants with entrance stage different than cero
                                speed_sc.append(0)
                            
                        power_wind_var[i][n][k]= speed_sc 
            
            # Save areas
            power_area.append(power_wind_var)
    
    power_area_energy = power(RnwArea,power_area,blocksData,scenarios,Param.stages,yearvector)
    
    # save results
    DataDictionary = {"power_area_energy":power_area_energy,"RnwArea":RnwArea}
    pickle.dump(DataDictionary, open( "savedata/windspeed_save.p", "wb" ) )

###############################################################################
        
def inputAvrSolarL(dict_data,Param):
    
    dict_solarL = pickle.load( open( "savedata/solar_large_save.p", "rb" ) )
    dict_sim = pickle.load( open( "savedata/format_sim_save.p", "rb" ) )
    
    solarLPlants = dict_data['Solar_large']
    indicesData = dict_data['indicesRad']
    indicesTemp = dict_data['TemperatureCell']
    blocksData = dict_data['blocksData']
    scenarios = Param.seriesForw
    rad_solar = dict_solarL['rad_solar']
    solarData = dict_data['SlargeData']
    numAreas = dict_data['numAreas']
    yearvector = dict_sim['yearvector']

    # save data
    power_area = [] 
    RnwArea = []

    # order of the information
    stationData = []; stationTemp = []
    for i in range(len(indicesData)):
        stationData.append(indicesData[i][0])
        stationTemp.append(indicesTemp[i][0])
    
    for area in range(numAreas):
        
        # Set of plants for each area
        solarP = 0; rad_temp = []; intensities=[]; indexS=[]; t_amb=[]
        for i in range(len(solarLPlants)):
            if solarData[8][i] == area+1:
                solarP += 1
                rad_temp.append(rad_solar[i])
                indexS.append(i)
                
                # matrix of intensities must be ordered to correspond with month
                indexP = stationData.index(solarData[0][i])
                indicesData[indexP].pop(0) # eliminating strings
                
                indexT = stationTemp.index(solarData[0][i])
                indicesTemp[indexT].pop(0) # eliminating strings
                
                intensity = np.resize(indicesData[indexP], [12,len(blocksData[0])])
                aux = 0; aux2 = 0; intensityPlant=[]; tambPlant=[]
                for n in range(Param.stages):
                    intensityPlant.append(intensity[n-aux2])
                    tambPlant.append(indicesTemp[indexT][n-aux2])
                    if ((n+1)/12)-1 == aux:
                        aux += 1; aux2 += 12
                
                intensities.append(intensityPlant)
                t_amb.append(tambPlant)
        
        if solarP != 0:
            # save areas with renewables
            
            RnwArea.append(area+1)
            
            # Inflow by blocks with short term variability
            power_solar_var = [[[[] for x in range(scenarios) ] for y in range(Param.stages)] for z in range(solarP)]
            for i in range(solarP):
                
                idx = indexS[i]
                efcc = solarData[10][idx]*solarData[11][idx]*solarData[4][idx]*solarData[2][idx]*solarData[3][idx]
                
                # solar power
                for n in range(Param.stages): 
                    
                    scenario_inflow = rad_temp[i][1][n]
                    
                    for k in range(scenarios): 
                        rad_sc = []
                        for j in range(len(blocksData[0])): 
                            
                            if scenario_inflow[k] > 0:
                                
                                mu = scenario_inflow[k]*intensities[i][n][j] # [Wh/m2]
                                tcell = t_amb[i][n] + ((mu/800)*(solarData[6][idx] - 20))
                                pdc = solarData[1][idx]*(mu/1000)*(1 - ((solarData[5][idx]/100) * (tcell - 25)))
                                if pdc > solarData[1][idx]:
                                    pdc = solarData[1][idx]
                                rad_sc.append(pdc*efcc)
                                
                            else:
                                # Plants with entrance stage different than cero
                                rad_sc.append(0)
                            
                        power_solar_var[i][n][k]= rad_sc 
            # Save areas
            power_area.append(power_solar_var)
    
    power_area_energy = power(RnwArea,power_area,blocksData,scenarios,Param.stages,yearvector)
    
    # save dictionary
    DataDictionary = {"power_area_energy":power_area_energy,"RnwArea":RnwArea}
    pickle.dump(DataDictionary, open( "savedata/solarradLarge.p", "wb" ) )
    
    ###########################################################################
    
def inputAvrSolarD(dict_data,Param):
    
    dict_solarD = pickle.load( open( "savedata/solar_dist_save.p", "rb" ) )
    dict_sim = pickle.load( open( "savedata/format_sim_save.p", "rb" ) )
    
    solarLPlants = dict_data['Solar_dist']
    indicesData = dict_data['indicesRad']
    blocksData = dict_data['blocksData']
    scenarios = Param.seriesForw
    rad_solar = dict_solarD['rad_solar']
    solarData = dict_data['SdistData']
    numAreas = dict_data['numAreas']
    yearvector = dict_sim['yearvector']

    # save data
    power_area = [] 
    RnwArea = []

    # order of the information
    stationData = []
    for i in range(len(indicesData)):
        stationData.append(indicesData[i][0])
    
    for area in range(numAreas):
        
        # Set of plants for each area
        solarP = 0; rad_temp = []; intensities=[]; indexS=[]
        for i in range(len(solarLPlants)):
            if solarData[4][i] == area+1:
                solarP += 1
                rad_temp.append(rad_solar[i])
                indexS.append(i)
                
                # matrix of intensities must be ordered to correspond with month
                indexP = stationData.index(solarData[0][i])
                indicesData[indexP].pop(0) # eliminating strings
                
                intensity = np.resize(indicesData[indexP], [12,len(blocksData[0])])
                aux = 0; aux2 = 0; intensityPlant=[]
                for n in range(Param.stages):
                    intensityPlant.append(intensity[n-aux2])
                    if ((n+1)/12)-1 == aux:
                        aux += 1; aux2 += 12
                
                intensities.append(intensityPlant)
                
        if solarP != 0:
            # save areas with renewables
            
            RnwArea.append(area+1)
            
            # Inflow by blocks with short term variability
            power_solar_var = [[[[] for x in range(scenarios) ] for y in range(Param.stages)] for z in range(solarP)]
            for i in range(solarP):
                
                idx = indexS[i]
                losses = (1-(solarData[5][idx]/100))*(1-(solarData[6][idx]/100))*(1-(solarData[7][idx]/100))*(1-(solarData[8][idx]/100))*(1-(solarData[9][idx]/100))*(1-(solarData[10][idx]/100))*(1-(solarData[11][idx]/100))
                rate_area = solarData[2][idx]
                
                # solar power
                for n in range(Param.stages): 
                    
                    scenario_inflow = rad_temp[i][1][n]
                    
                    for k in range(scenarios): 
                        rad_sc = []
                        for j in range(len(blocksData[0])): 
                            
                            if scenario_inflow[k] > 0:
                                
                                mu = scenario_inflow[k]*intensities[i][n][j] # [Wh/m2]
                                pdc = mu*solarData[1][idx]*rate_area
                                rad_sc.append(pdc*losses)
                                
                            else:
                                # Plants with entrance stage different than cero
                                rad_sc.append(0)
                            
                        power_solar_var[i][n][k]= rad_sc
                    
                    # growth rate
                    rate_area = rate_area * (1 + (solarData[12][idx]/100))
                    
            # Save areas
            power_area.append(power_solar_var)
    
    power_area_energy = power(RnwArea,power_area,blocksData,scenarios,Param.stages,yearvector)
    
    # save dictionary
    DataDictionary = {"power_area_energy":power_area_energy,"RnwArea":RnwArea}
    pickle.dump(DataDictionary, open( "savedata/solarradDist.p", "wb" ) )
