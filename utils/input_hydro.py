def inputhydro(dict_data):
    
    import pickle
    dict_sim = pickle.load( open( "savedata/format_sim_save.p", "rb" ) )
    
    yearvec = dict_sim['yearvector']
    hydroPlants = dict_data['hydroPlants']
    volData = dict_data['volData']
    expData = dict_data['expData']
    
    # hydro limits
    numReservoirs = len(hydroPlants) # Reservoirs asociated with hydro plants
    prodFactor = [x*(1e6/3600) for x in volData[4]] # Production factor of hydro plants
    u_hat = [] # Limits in the volume turbined at each stage by each hydro plant
    for i in range(numReservoirs):
        # if some reservoirs are not linked to a generation plant
        if prodFactor[i] == 0 or volData[3] == 0:
            u_hat2 = [x*(volData[5][i]*3600*1e-6) for x in yearvec[0:]]
            u_hataux = []    
            for j in range(len(u_hat2)):
                aux = u_hat2[j] 
                if volData[6][i] > j+1:
                    aux = 0
                u_hataux.append(aux*(1-(volData[14][i]/100)))
        # otherwise
        else:
            u_hat1 = [x*(volData[3][i]/prodFactor[i]) for x in yearvec[0:]]
            u_hat2 = [x*(volData[5][i]*3600*1e-6) for x in yearvec[0:]]
            u_hataux = []    
            for j in range(len(u_hat1)):
                aux = min(u_hat1[j],u_hat2[j]) 
                if volData[6][i] > j+1:
                    aux = 0
                u_hataux.append(aux*(1-(volData[14][i]/100)))
        u_hat.append(u_hataux)
    
    # hydro limits - Expansion modifications
    prodFactor = [[] for x in range(numReservoirs)] # Limits in the volume turbined at each stage by each hydro plant
    for i in range(numReservoirs):
        for z in range(len(yearvec)):
            prodFactor[i].append( volData[4][i] * (1e6/3600) ) # Production factor of hydro plants
    
    if len(expData[0]) > 0:
        
        for i in range(len(expData[0])):
            index = hydroPlants.index(expData[0][i])
            fchange = [x*0+(expData[2][i]*(1e6/3600)) for x in prodFactor[index][expData[4][i]-1:]]
            prodFactor[index][expData[4][i]-1:] = fchange
            
            # modifications in u_limits
            u_hat1 = [x*(expData[1][i]/(expData[2][i]*(1e6/3600))) for x in yearvec[expData[4][i]-1:]]
            u_hat2 = [x*(expData[3][i]*3600*1e-6) for x in yearvec[expData[4][i]-1:]]
            u_hataux = []    
            for j in range(len(u_hat1)):
                aux = min(u_hat1[j],u_hat2[j]) 
                u_hataux.append(aux*(1-(expData[7][i]/100)))
            u_hat[index][expData[4][i]-1:] = u_hataux
            
    
    # Save  OyM costs
    oymcost = []; volmin = []; volmax = []; tdownstream = []; sdownstream = []
    for n in range(len(hydroPlants)): 
        oymcost.append(float(volData[8][n]))
        volmin.append(float(volData[1][n]))
        volmax.append(float(volData[2][n]))
        for z in range(len(hydroPlants)):
            if hydroPlants[z] == volData[9][n]: 
                tdownstream.append([hydroPlants[n],hydroPlants[z]])
            if hydroPlants[z] == volData[10][n]: 
                sdownstream.append([hydroPlants[n],hydroPlants[z]])              
    
    # export data
    DataDictionary = {"u_limit":u_hat,"prodFactor":prodFactor,"oymcost":oymcost,"volmin":volmin,
                      "volmax":volmax,"T-downstream":tdownstream,"S-downstream":sdownstream}
    pickle.dump(DataDictionary, open( "savedata/hydro_save.p", "wb" ) )
    
    # return DataDictionary