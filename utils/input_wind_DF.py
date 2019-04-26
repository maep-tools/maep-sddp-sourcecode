def inputDFWind(dict_data,Param):
    
    import pickle
    import numpy as np
    
    dict_wind = pickle.load( open( "savedata/wind_save0.p", "rb" ) )
    dict_sim = pickle.load( open( "savedata/format_sim_save.p", "rb" ) )
    
    windPlants = dict_data['windPlants']
    indicesData = dict_data['indicesData']
    blocksData = dict_data['blocksData']
    scenarios = Param.seriesForw # dict_sim['scenarios'] 
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
        
        if windP is not 0:
            # save areas with renewables
            
            RnwArea.append(area+1)
            
            # Inflow by blocks with short term variability
            power_wind_var = [[[[] for x in range(scenarios) ] for y in range(Param.stages)] for z in range(windP)]
            for i in range(windP):
                
                # number of turbines
                idx = index[i]
                numTbn = windData[0][idx] / ( (3.1416/8)*windData[2][idx]*windData[13][idx]*(windData[4][idx]**2)*(windData[5][idx]**3) / 1e6)
                
                # wind power
                 
                deviation = windData[10][idx]/100
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
                                dev = (deviation * mu)**0.5
                                sample = np.random.normal(mu, dev, Param.dist_samples)
                                
                                sample_power = []
                                for count in range(Param.dist_samples):
                                    
                                    sampl_val = (sample[count]**3 )*o_idx * windData[1][idx]
                                    
                                    if sampl_val > p_max or sampl_val <= p_min:
                                        sample_power.append(0)
                                    elif sampl_val > p_nom and sampl_val <= p_max:
                                        sample_power.append(p_nom)
                                    elif sampl_val > p_min and sampl_val <= p_nom:
                                        sample_power.append(sampl_val)
                                    
                                speed_sc.append(sample_power)
                                
                            else:
                                # Plants with entrance stage different than cero
                                speed_sc.append([0]*Param.dist_samples)
                            
                        power_wind_var[i][n][k]= speed_sc 
            
            # Save areas
            power_area.append(power_wind_var)
    
    ###########################################################################
    
    # Areas - energy - samples
    power_area_energy = []
    for area in range(len(RnwArea)):
        ene_area = power_area[area]
        
        power_temp = [[[[] for x in range(len(blocksData[0])) ] for y in range(scenarios)] for z in range(Param.stages)]
        
        for n in range(Param.stages): 
            for k in range(scenarios): 
                for j in range(len(blocksData[0])): 
                    sum_p = [0]*Param.dist_samples
                    for i in range(len(ene_area)):
                        sum_p = [sum(x) for x in zip(sum_p, ene_area[i][n][k][j])]
                    
                    energy_area = [ int(x * yearvector[n]*blocksData[0][j]) for x in sum_p]
                    power_temp[n][k][j]= energy_area
                    
        # save data areas
        power_area_energy.append(power_temp)

    ###########################################################################
    
    DataDictionary = {"power_area_energy":power_area_energy,"RnwArea":RnwArea}
    pickle.dump(DataDictionary, open( "savedata/windspeed_save.p", "wb" ) )
    
