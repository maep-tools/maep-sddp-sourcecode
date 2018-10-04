def aggr_energy(dict_data, Param):
    
    import pickle
    import numpy as np
    
    from utils.mipproblem import fisrt_vec, pelp_vec
    
    dict_wind = pickle.load( open( "savedata/windspeed_save.p", "rb" ) )
    # dict_format = pickle.load(open("savedata/format_save.p", "rb"))
    
    # df_demand = dict_format['demand']
    blocksData = dict_data['blocksData']
    RnwArea = dict_wind['RnwArea']
    power_area_energy = dict_wind['power_area_energy']
    
    ###########################################################################
    
    # p_efficient points calculation

    pefficient_vec = [[[] for y in range(Param.seriesBack)] for z in range(Param.stages)]
    
    for n in range(Param.stages): 
        for k in range(Param.seriesBack): 
            
            sc_st_vec = []
            for area in range(len(RnwArea)):
                for j in range(len(blocksData[0])):
                    # residual load
                    #load = int(1e6 * df_demand[RnwArea[area] -1][n][j])
                    #res_load = [load-x for x in power_area_energy[area][n][k][j]]
                    #sc_st_vec.append(res_load)
                    sc_st_vec.append(power_area_energy[area][n][k][j])
            
            perc = []
            for i in range(len(sc_st_vec)):
                aux = np.array(sc_st_vec[i])
                pc_vec = np.percentile(aux, (1-Param.eps_all)*100)
                perc.append(int(pc_vec))
                
            # sc_st_vec re-arranging
            weightvec = []
            for i in range(Param.w_free_samples):
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
                    probvec.append(1/Param.w_free_samples)
                else:
                    index = weightvec2.index(item)
                    probvec[index] = probvec[index] + (1/Param.w_free_samples)

            maxD = weightvec2[0]
            for i in range(len(weightvec2)-1):
                for j in range(len(maxD)):
                    if weightvec2[i+1][j] > maxD[j]:
                        maxD[j] = weightvec2[i+1][j]
            
            f_plep = fisrt_vec(weightvec2,probvec,maxD,Param.eps_all)   
                       
            for i in range(int(Param.w_free_samples * 0.1)):
                long_i = len(f_plep)
                vec_iter = pelp_vec(weightvec2,probvec,f_plep,long_i,maxD,Param.eps_all)
                if vec_iter[0] is None:
                    break
                else:
                    if vec_iter not in f_plep: 
                        f_plep.append(vec_iter)

            # save p-efficient points 
            pefficient_vec[n][k]= f_plep

    
    ###########################################################################
    
    #DataDictionary = {"power_area_energy":power_area_energy,"RnwArea":RnwArea}
    #pickle.dump(DataDictionary, open( "savedata/windspeed_save.p", "wb" ) )
