
import pickle
    
def inputwindSet(dict_data,Param):
    
    from utils.input_wind import inputwind
    
    numAreas = dict_data['numAreas']
    
    if Param.wind_model2 is True:
            
        windRPlants = dict_data['windRPlants']
        windRData = dict_data['windRData']
        inflowRealData = dict_data['inflowRealData']
        indcStage = 11; indcArea = 12
        
        inputwind(indcStage,indcArea,windRPlants,windRData,[[]],inflowRealData,numAreas,
                  Param.stages,1,Param)
        
    else:
            
        windPlants = dict_data['windPlants']
        windData = dict_data['windData']
        expWindData = [[]] # dict_data['expWindData'] Not operative yet
        inflowWindData = dict_data['inflowWindData']
        indcStage = 6; indcArea = 8
        
        inputwind(indcStage,indcArea,windPlants,windData,expWindData,inflowWindData,
                  numAreas,Param.stages,0,Param)
 
###############################################################################
        
def inputwind(indcStage,indcArea,windPlants,windData,expWindData,inflowWindData,
              numAreas,stages,var,Param):
    
    import numpy as np
    from utils.paramvalidation import scenariosvalidation
    
    dict_sim = pickle.load( open( "savedata/format_sim_save.p", "rb" ) )
    
    scenariosWind = max(inflowWindData[1][1:])
    scenariosvalidation(scenariosWind,Param,'Wind speed')
    yearvector = dict_sim['yearvector']
    
    speed_wind = [[[] for _ in range(2) ] for _ in range(len(windPlants))]
    
    # Production energy limits
    numFarms = len(windPlants) # Wind plants
    #prodFactor = [x for x in windData[1]] # Production losses of wind plants
    w_hat = [] # Limits of energy at each stage
    
    if numFarms > 0: # at least one wind power plant in the system
        for i in range(numFarms):
            # Limits of generation cosidering losses
            w_hat1 = [x * windData[0][i] for x in yearvector[0:]]
            for j in range(len(w_hat1)):
                if windData[indcStage][i] > j+1:
                    w_hat1[j] = 0
            w_hat.append(w_hat1)
        
        # Expansion of capacity of wind plants
        if len(expWindData[0]) > 0:
            
            for i in range(len(expWindData[0])): # loop in modificated plants
                index = windPlants.index(expWindData[0][i])
                stagemod = expWindData[1][i]
                # Limits of generation cosidering losses
                gmaxplant = [x * expWindData[2][i] * expWindData[6][i] for x in yearvector[stagemod-1:]]
                
                for z in range(stagemod,stages+1):
                    w_hat[index][z-1] = gmaxplant[z-stagemod]
                
    hat_area = [[0]*len(yearvector) for _ in range(numAreas) ] 
    for i in range(numFarms):
        areafarm = windData[indcArea][i]
        hat_area[areafarm-1] = [sum(x) for x in zip(hat_area[areafarm-1], w_hat[i])]
    
    # Wind speed
    for i in range(stages):
        # Series Wind
        for k in range(2,2+len(windPlants)):
            
            stage_wind = inflowWindData[k][scenariosWind*i+1:scenariosWind*i+1+scenariosWind]
            if windData[indcStage][k-2] > i+1: # initial stage for inflows
                stage_wind[:] = [x*0 for x in stage_wind]
            aux_wind = np.hstack((speed_wind[k-2][1], stage_wind))        
            speed_wind[k-2][1] = aux_wind
            
    # wind inflow series
    for i in range(len(windPlants)):
        aux_resize_s = np.resize(speed_wind[i][1], [stages,scenariosWind]) 
        speed_wind[i][0] = inflowWindData[2+i][0] 
        speed_wind[i][1] = aux_resize_s  
    
    # export data
    DataDictionary = {"w_limit":w_hat, "speed_wind":speed_wind}
    pickle.dump(DataDictionary, open( "savedata/wind_save"+str(var)+".p", "wb" ) )
    
    # export data
    DataDictionary = {"hat_area":hat_area}
    pickle.dump(DataDictionary, open( "savedata/wind_hat_"+str(var)+".p", "wb" ) )
    
###############################################################################
    
def inputInflowWind(dict_data,Param):
                    
    stages = Param.stages
    eps_area = Param.eps_area
    eps_all = Param.eps_all
    
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

    #import numpy as np
    from scipy.stats import norm
    import numpy as np
    
    power_area = [] # pmax = [0]*numAreas
    RnwArea = []
    for col in range(len(indicesData)):
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
                for n in range(stages):
                    intensityPlant.append(intensity[n-aux2])
                    if ((n+1)/12)-1 == aux:
                        aux += 1; aux2 += 12
                
                intensities.append(intensityPlant)
        
        if windP != 0:
            # save areas with renewables
            RnwArea.append(area+1)
            
            # Inflow by blocks with short term variability
            power_wind_var = [[[[] for x in range(scenarios) ] for y in range(stages)] for z in range(windP)]
            for i in range(windP):
                
                # number of turbines
                idx = index[i]
                numTbn = windData[0][idx] / ( (3.1416/8)*windData[2][idx]*windData[13][idx]*(windData[4][idx]**2)*(windData[5][idx]**3) / 1e6)
                
                # wind power
                 
                deviation = windData[10][idx]/100
                o_idx = (3.1416/8)*windData[2][idx]*windData[3][idx]*(windData[4][idx]**2)*numTbn
                p_max = (windData[12][idx]**3 + 3*deviation*windData[12][idx]**2)*o_idx/1e6
                p_min = (windData[11][idx]**3 + 3*deviation*windData[11][idx]**2)*o_idx/1e6
                p_nom = (windData[5][idx]**3 + 3*deviation*windData[5][idx]**2)*o_idx/1e6
                
                for n in range(stages): 
                    scenario_inflow = speed_wind_temp[i][1][n]
                    for k in range(scenarios): 
                        speed_sc = []
                        for j in range(len(blocksData[0])): 
                            
                            if scenario_inflow[k] > 0:
                                
                                mu = scenario_inflow[k]*intensities[i][n][j]
                                var = deviation * mu
                                
                                # mean and variance
                                p_m = (mu**3 + 3*mu*var)*o_idx/1e6
                                p_var = 3*var*( 3*(mu**4) + 12*var*(mu**2) + 5*(var**2) )*((o_idx/1e6)**2)
                                
                                # Truncated
                                cdf_out = norm.cdf((windData[12][idx]-mu)/(var**0.5))
                                cdf_in = norm.cdf((windData[11][idx]-mu)/(var**0.5))
                                
                                # probability 1 - no wind power
                                Fp0 = cdf_in + (1-cdf_out)
                                
                                if Fp0 >= 1:
                                    speed_sc.append([0]*4)
                                    
                                else:
                                    # truncation correction
                                    normA = (-p_m)/(p_var**0.5); normB = (p_max-p_m)/(p_var**0.5)
                                    c_normA = norm.pdf(normA)
                                    c_normB = norm.pdf(normB)
                                    
                                    p_m2 = (p_m - ((p_var**0.5)*((c_normB-c_normA)/(1-Fp0)))) * windData[1][idx]
                                    
                                    #speed_sc.append([p_m2,p_var,p_min,p_nom])
                                    
                                    if p_m2 > p_nom and p_m2 <= p_max:
                                        speed_sc.append([p_nom,0,p_min,p_nom])
                                        
                                    elif p_m2 <= p_min or p_m2 > p_max:
                                        speed_sc.append([0,0,p_min,p_nom])
                                        
                                    elif p_m2 > p_min and p_m2 <= p_nom:
                                        p_var2 = p_var * ( 1 + (((normA*c_normA)-(normB*c_normB))/(1-Fp0)) - ((c_normA-c_normB)/(1-Fp0))**2)
                                        speed_sc.append([p_m2,p_var2,p_min,p_nom])
                                        
                            else:
                                # Plants with entrance stage different than cero
                                speed_sc.append([0]*4)
                            
                        power_wind_var[i][n][k]= speed_sc 
            
        else:
            # Inflow by blocks with short term variability
            power_wind_var = [[[[[0]*4 for j in range(len(blocksData[0]))] for x in range(scenarios) ] for y in range(stages)] for z in range(1)]
            
        # Save areas
        power_area.append(power_wind_var)
    
    ###########################################################################
    
    # Areas - quantile
    power_area_quant = []
    for area in range(numAreas):
        ene_area = power_area[area]
        
        power_temp = [[[[] for x in range(len(blocksData[0])) ] for y in range(scenarios)] for z in range(stages)]
        
        for n in range(stages): 
            #print('stage', n)
            for k in range(scenarios):
                #print('scenario',k)
                for j in range(len(blocksData[0])): 
                    sum_p = [0]*4
                    #print('block',j)
                    for i in range(len(ene_area)):
                        sum_p = [sum(x) for x in zip(sum_p, ene_area[i][n][k][j])]
                        #print('area',i)
                    
                    if sum_p[1] > 0:
                        inf_sum = (-sum_p[0])/(sum_p[1]**0.5)
                        sup_sum = (sum_p[3]-sum_p[0])/(sum_p[1]**0.5)
                        
                        # quantile
                        q_low = norm.cdf(inf_sum)
                        q_upp = norm.cdf(sup_sum)
                        int_quan = q_low + eps_area*(q_upp-q_low)
                        
                        # quantile
                        f_area = norm.ppf(int_quan)
                        f_quan = sum_p[0] + f_area*(sum_p[1]**0.5)
                        
                        # results energy
                        energy_quan = f_quan*yearvector[n]*blocksData[0][j]
                        power_temp[n][k][j]= energy_quan
                    
                    else:
                        # No power plants in the area
                        power_temp[n][k][j]= sum_p[0]*yearvector[n]*blocksData[0][j]
                    
        # save data areas
        power_area_quant.append(power_temp)

    ###########################################################################
    
    # General - quatile
    power_general_quant = [[[[] for x in range(len(blocksData[0])) ] for y in range(scenarios)] for z in range(stages)]

    for n in range(stages): 
        for k in range(scenarios): 
            for j in range(len(blocksData[0])): 
                sum_p = [0]*4
                for area in range(numAreas):
                    lenwind= len(power_area[area])
                    for i in range(lenwind):
                        sum_p = [sum(x) for x in zip(sum_p, power_area[area][i][n][k][j])]
                
                if sum_p[1] > 0:
                    inf_sum = (-sum_p[0])/(sum_p[1]**0.5)
                    sup_sum = (sum_p[3]-sum_p[0])/(sum_p[1]**0.5)
                    
                    # quantile
                    q_low = norm.cdf(inf_sum)
                    q_upp = norm.cdf(sup_sum)
                    int_quan = q_low + eps_all*(q_upp-q_low)
                    
                    # quantile
                    f_all = norm.ppf(int_quan)
                    f_quan = sum_p[0] + f_all*(sum_p[1]**0.5)
                    
                    # results energy
                    energy_quan = f_quan*yearvector[n]*blocksData[0][j]
                    power_general_quant[n][k][j]= energy_quan
        
                else:
                    # No power plants in the system
                    power_general_quant[n][k][j]= sum_p[0]*yearvector[n]*blocksData[0][j]
    
    ###########################################################################
    
    DataDictionary = {"windenergy_area":power_area_quant,"windenergy_all":power_general_quant,
                      "RnwArea":RnwArea}
    
    pickle.dump(DataDictionary, open( "savedata/windspeed_save.p", "wb" ) )
    
    #return DataDictionary

###############################################################################
    
def energyRealWind(dict_data,seriesBack,stages):
    
    from utils.efunction import prepareCurves, prepareFactors # , e_areas 
    
    dict_R_wind = pickle.load( open( "savedata/wind_save1.p", "rb" ) )
    dict_windmat = pickle.load( open( "savedata/data_windmat.p", "rb" ) )
    
#    numAreas = dict_data['numAreas']
#    numBlocks = dict_format['numBlocks']
#    subsystem =[ [ [ [ [] for i in range(numBlocks)] for j in range(seriesBack)] for k in range(stages)] for l in range(numAreas)] 
#    allsystem = [ [ [ [] for i in range(numBlocks)] for j in range(seriesBack)] for k in range(stages)] 
    
    curvesData = dict_data['ctData_act']
    windFarmData = dict_data['windRData']
    dictRwind = dict_R_wind['speed_wind']
    windmat = dict_windmat['windmat']
    
    curvesData,curvesN,entrance = prepareCurves(windFarmData,curvesData,dictRwind)
    factores = prepareFactors(windFarmData,windmat)
    
#    for x in range(stages):
#        for y in range(seriesBack):
#            for z in range(numBlocks):
#                energy_areas = e_areas(dictRwind,windFarmData,curvesData,curvesN,factores,entrance,x,y,z,numAreas)
#                for a in range(numAreas):
#                    subsystem[a][x][y][z] = energy_areas[a]
#    
#    #Sumando para hallar totales
#    for et in range(stages):
#        for es in range(seriesBack):
#            for b in range(numBlocks):
#                total = 0
#                for a in range(numAreas):
#                    total = total + subsystem[a][et][es][b]
#                allsystem[et][es][b] = total
    
    #return subsystem, allsystem
    return factores