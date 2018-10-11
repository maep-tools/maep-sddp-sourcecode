def aggr_energy(dict_data, Param):
    
    import pickle
    import numpy as np
    
    from utils.mipproblem import fisrt_vec, pelp_vec
    
    dict_wind = pickle.load( open( "savedata/windspeed_save.p", "rb" ) )
    dict_solD = pickle.load( open( "savedata/solarradDist.p", "rb" ) )
    dict_solL = pickle.load( open( "savedata/solarradLarge.p", "rb" ) )
    dict_sim = pickle.load( open( "savedata/format_sim_save.p", "rb" ) )
    dict_format = pickle.load(open("savedata/format_save.p", "rb"))
    
    # data
    blocksData = dict_data['blocksData']
    numAreas = dict_data['numAreas']
    scenarios = dict_sim['scenarios']
    df_demand = dict_format['demand']
    
    ###########################################################################
    
    # renewables area
    wind_area = dict_wind['RnwArea']
    sol_dist = dict_solD['RnwArea']
    sol_large = dict_solL['RnwArea']
    RnwArea = list(set( wind_area + sol_dist + sol_large))
    
    wind_energy = dict_wind['power_area_energy']
    solD_energy = dict_solD['power_area_energy']
    solL_energy = dict_solL['power_area_energy']
    
    # Areas - energy - samples
    power_area_energy = []
    for area in range(len(RnwArea)):
        
        ene_area = []
        if RnwArea[area] in wind_area: 
            indexP = wind_area.index(RnwArea[area])
            ene_area.append(wind_energy[indexP])
        if RnwArea[area] in sol_dist:
            indexP = sol_dist.index(RnwArea[area])
            ene_area.append(solD_energy[indexP])
        if RnwArea[area] in sol_large:    
            indexP = sol_large.index(RnwArea[area])
            ene_area.append(solL_energy[indexP])
            
        power_temp = [[[[] for x in range(len(blocksData[0])) ] for y in range(scenarios)] for z in range(Param.stages)]
        
        for n in range(Param.stages): 
            for k in range(scenarios): 
                for j in range(len(blocksData[0])): 
                    sum_p = [0]*Param.dist_samples
                    for i in range(len(ene_area)):
                        sum_p = [sum(x) for x in zip(sum_p, ene_area[i][n][k][j])]
                    
                    power_temp[n][k][j]= sum_p
                    
        # save data areas
        power_area_energy.append(power_temp)
        
    ###########################################################################
    # p_efficient points calculation

    pefficient_vec = [[[] for y in range(Param.seriesBack)] for z in range(Param.stages)]
    plep_count = 2 # counter for pleps set
    
    for n in range(Param.stages): 
        for k in range(Param.seriesBack): 
            
            sc_st_vec = []
            for area in range(len(RnwArea)):
                for j in range(len(blocksData[0])):
                    # residual load
                    load = 1e6 * df_demand[RnwArea[area] -1][n][j]
                    res_load = [int((load-x)/1e3) for x in power_area_energy[area][n][k][j]]
                    sc_st_vec.append(res_load)
                    #sc_st_vec.append(power_area_energy[area][n][k][j])
            
            perc = []
            for i in range(len(sc_st_vec)):
                aux = np.array(sc_st_vec[i])
                pc_vec = np.percentile(aux, (1-Param.eps_all)*100)
                perc.append(int(pc_vec))
                
            # sc_st_vec re-arranging
            weightvec = []
            for i in range(Param.dist_samples):
                aux2 = []
                for j in range(len(blocksData[0])*len(RnwArea)):
                    if perc[j] >= sc_st_vec[j][i]:
                        aux2.append(perc[j])
                    else:
                        aux2.append(sc_st_vec[j][i])
                weightvec.append(aux2)
                
            weightvec2 = []; probvec = []
            for item in weightvec:
                if item not in weightvec2:
                    weightvec2.append(item)
                    probvec.append(1/Param.dist_samples)
                else:
                    index = weightvec2.index(item)
                    probvec[index] = probvec[index] + (1/Param.dist_samples)

            maxD = weightvec2[0]
            for i in range(len(weightvec2)-1):
                for j in range(len(maxD)):
                    if weightvec2[i+1][j] > maxD[j]:
                        maxD[j] = weightvec2[i+1][j]
            
            f_plep = fisrt_vec(weightvec2,probvec,Param.eps_all)   
            
            for i in range(int(Param.dist_samples * 0.2)):
                long_i = len(f_plep)
                vec_iter = pelp_vec(weightvec2,probvec,f_plep,long_i,maxD,Param.eps_all)
                if vec_iter[0] is None:
                    break
                else:
                    if vec_iter not in f_plep: 
                        f_plep.append(vec_iter)
                        # count the points
                        if i+2 > plep_count: plep_count = i+2

            # save p-efficient points 
            pefficient_vec[n][k]= f_plep

    ###########################################################################
    # p_efficient points matrix
    
    ppoints_vec = [[[[[] for j in range(len(blocksData[0]))] for x in range(numAreas)] for y in range(Param.seriesBack)] for z in range(Param.stages)]
    
    for n in range(Param.stages): 
        for k in range(Param.seriesBack):
            numPaux = len(pefficient_vec[n][k])
            for y in range(len(RnwArea)): 
                for z in range(len(blocksData[0])):
                    block_plep = []
                    for x in range(plep_count):
                        if x+1 <= numPaux:
                            dem = pefficient_vec[n][k][x][(y*len(blocksData[0]))+z] / 1e3
                            block_plep.append(dem)
                        else:
                            block_plep.append(df_demand[RnwArea[y]-1][n][z])
                    ppoints_vec[n][k][RnwArea[y]-1][z] = block_plep
                    
    # areas without renewables
    for n in range(Param.stages): 
        for k in range(Param.seriesBack):
            numPaux = len(pefficient_vec[n][k])
            for y in range(numAreas): 
                if y+1 not in RnwArea:
                    for z in range(len(blocksData[0])):
                        block_plep = [df_demand[y][n][z]] * plep_count
                        ppoints_vec[n][k][y][z] = block_plep
                        
    ###########################################################################
    
    DataDictionary = {"p_points":ppoints_vec,"plepcount": plep_count,"pefficient_vec":pefficient_vec}
    pickle.dump(DataDictionary, open( "savedata/pleps_save.p", "wb" ) )
