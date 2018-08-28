def ybus(stages):
    
    import numpy as np
    import pickle
    
    # Load the dictionary back from the pickle file
    dict_data = pickle.load(open("savedata/data_save.p", "rb"))
    dict_format = pickle.load(open("savedata/format_save.p", "rb"))
    
    demandArea = dict_format['demandArea']
    hydroArea = dict_data['volData'][11]
    thermalArea = dict_data['thermalData'][3]
    windArea = dict_data['windData'][8]
    storageArea = dict_data['battData'][9]
    
    # nodes with injection or consuption
    nodesBaln = demandArea+hydroArea+thermalArea+windArea+storageArea
    output = []
    for x in nodesBaln:
        if x not in output:
          output.append(x)
      
    busesData = dict_data['areasData'][1]
    linesData = dict_data['linesData']
    expLines = dict_data['expLines']
    
    setLines = []
    for i in range(len(linesData)):
        setLines.append(linesData[i][0:2])
        
    # calculate the suscentance matrix
    matrixInc = np.zeros((len(busesData), len(linesData)))
    matrixSct = np.zeros((len(linesData), len(linesData)))
    
    for bus in range(len(linesData)):
        matrixInc[linesData[bus][0]-1,bus] = -1
        matrixInc[linesData[bus][1]-1,bus] = 1
        b = -linesData[bus][6]/(linesData[bus][5]**2 + linesData[bus][6]**2)
        matrixSct[bus,bus] = b
        
    trasInc = np.transpose(matrixInc)
    matrixbeta = matrixInc.dot(matrixSct.dot(trasInc))
    
    matrixbeta = np.delete(matrixbeta, (0), axis=0)
    matrixbeta = np.delete(matrixbeta, (0), axis=1)
    
    # suceptance transpose
    trasbeta = np.linalg.inv(matrixbeta)
    
    # null row and colum
    trasbeta = np.hstack((np.zeros((len(busesData)-1,1)), trasbeta ))
    trasbeta = np.vstack((np.zeros(len(busesData)), trasbeta ))
    
    # intensities
    beta = matrixSct.dot(trasInc.dot(trasbeta))
    
    lineBus = []
    for (x,y), value in np.ndenumerate(beta):
        if abs(beta[x,y]) < 0.01:
            beta[x,y] = 0
        if abs(beta[x,y]) >= 0.01:
            if y+1 in output:
                lineBus.append([x+1,y+1])
        
    # save matrix
    stage_beta = []
    stage_linebus = []
    for i in range(stages):
            stage_beta.append(beta)
            stage_linebus.append(lineBus)
            
    if len(expLines) > 0:
        for i in range(len(expLines)):
            
            if expLines[i][2] <= stages:

                b = -expLines[i][7]/(expLines[i][6]**2 + expLines[i][7]**2)
                indexLn = setLines.index([expLines[i][0],expLines[i][1]])
                
                matrixSct[indexLn,indexLn] = b
                    
                trasInc = np.transpose(matrixInc)
                matrixbeta = matrixInc.dot(matrixSct.dot(trasInc))
                
                matrixbeta = np.delete(matrixbeta, (0), axis=0)
                matrixbeta = np.delete(matrixbeta, (0), axis=1)
                
                # suceptance transpose
                trasbeta = np.linalg.inv(matrixbeta)
                
                # null row and colum
                trasbeta = np.hstack((np.zeros((len(busesData)-1,1)), trasbeta ))
                trasbeta = np.vstack((np.zeros(len(busesData)), trasbeta ))
                
                # intensities
                beta = matrixSct.dot(trasInc.dot(trasbeta))
                
                lineBus = []
                for (x,y), value in np.ndenumerate(beta):
                    if abs(beta[x,y]) < 0.01:
                        beta[x,y] = 0
                    if abs(beta[x,y]) > 0.01:
                        if y+1 in output:
                            lineBus.append([x+1,y+1])
                
                for stage in range(expLines[i][2],stages+1):
                    
                    stage_beta[stage-1] = beta
                    stage_linebus[stage-1] = lineBus
    
    # export data
    DataDictionary = {"matrixbeta":stage_beta,"matrixLineBus":stage_linebus}
    
    pickle.dump(DataDictionary, open( "savedata/matrixbeta_save.p", "wb" ) )