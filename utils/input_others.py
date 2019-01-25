
import pickle

def inputbatteries(dict_data,stages):
    
    dict_sim = pickle.load( open( "savedata/format_sim_save.p", "rb" ) )
    
    yearvec = dict_sim['yearvector']
    batteries = dict_data['batteries']
    battData = dict_data['battData']
#    expBttData = [[]] # dict_data['expBttData'] Not operative yet
    
    numBatteries = len(batteries) # batteries
    b_hat = []; b_storage_hat = [] # Limits in the energy delivered at each stage by each batterie
    for i in range(numBatteries):
        b_hat1 = [x*battData[3][i] for x in yearvec[0:]]
        b_hat2 = [x*(battData[5][i]*3600) for x in yearvec[0:]]
        b_hataux = []; b_storage_aux = []    
        for j in range(len(b_hat1)):
            aux = min(b_hat1[j],b_hat2[j]) 
            aux2 = b_hat1[j] # battData[3][i] * battData[2][i]  # max storage
            aux3 = battData[3][i] * battData[2][i]  # max storage
            if battData[6][i] > j+1: # initial stage
                aux = 0; aux2 = 0; aux3 = 0
            b_hataux.append(aux * (1-(battData[11][i]/100)))
            b_storage_aux.append([aux2,aux3])
        b_hat.append(b_hataux); b_storage_hat.append(b_storage_aux)
    
    b_area = []
    for n in range(len(batteries)): 
        b_area.append(battData[9][n])
    
    # Expansion of batteries capacity
#    if len(expBttData[0]) > 0:
#        
#        for i in range(len(expBttData[0])): # loop in modificated plants
#            index = batteries.index(expBttData[0][i])
#            stagemod = expBttData[1][i]
#            for z in range(stagemod,stages+1):
#                b_storage_hat[index][z-1][0] = expBttData[2][i]
                
    # export data
    DataDictionary = {"b_limit":b_hat,"b_area":b_area, "b_storage":b_storage_hat}
    
    pickle.dump(DataDictionary, open( "savedata/batt_save.p", "wb" ) )
    
    #return DataDictionary

###############################################################################

def inputlines(Param,dict_data):

    dict_sim = pickle.load( open( "savedata/format_sim_save.p", "rb" ) )
    
    yearvector = dict_sim['yearvector']
    numAreas = dict_data['numAreas']
    linesData = dict_data['linesData']
    expLines = dict_data['expLines']
    gateLines = dict_data['gatesData']
    
    # Lines limits
    limitStages = []
    for stage in range(Param.stages):
    
        LinesMatrix = [[0 for x in range(numAreas)] for y in range(numAreas)] 
        for z in range(len(linesData)):
            LinesMatrix[int(linesData[z][0])-1][int(linesData[z][1])-1]=linesData[z][2]*yearvector[stage]
            LinesMatrix[int(linesData[z][1])-1][int(linesData[z][0])-1]=linesData[z][3]*yearvector[stage]
        
        limitStages.append(LinesMatrix)
    
    if len(expLines) > 0:
        
        for i in range(len(expLines)):
            
            if expLines[i][2] <= Param.stages:
                
                for stage in range(expLines[i][2],Param.stages+1):
                    
                    limitStages[stage-1][int(expLines[i][0])-1][int(expLines[i][1])-1]= expLines[i][3]*yearvector[stage-1]
                    limitStages[stage-1][int(expLines[i][1])-1][int(expLines[i][0])-1]= expLines[i][4]*yearvector[stage-1]
    
    # Define the flow gates
    numGates = len(gateLines)
    sets = [gateLines[x][0] for x in range(numGates)]
    setlines = []
    gateslimit = [[] for x in range(numGates)]

    if Param.flow_gates is True:
        for x in range(numGates):
            for stage in range(Param.stages):
                if stage+1 >= gateLines[x][2] and stage+1 <= gateLines[x][3]:
                    limit = gateLines[x][1]*yearvector[stage]
                    gateslimit[x].append(limit)
                else:
                    gateslimit[x].append(9999999)
            for y in range(sets[x]):
                nodo1 = gateLines[x][4+(y*2)]
                nodo2 = gateLines[x][5+(y*2)]
                for z in range(len(linesData)):
                    line = [linesData[z][0],linesData[z][1]]
                    if [nodo1,nodo2] == line:
                        setlines.append([x+1,z+1,nodo2,1])
                    if [nodo2,nodo1] == line:
                        setlines.append([x+1,z+1,nodo2,-1])
    # export data
    DataDictionary = {"l_limits":limitStages,"gatesets":setlines,"gateslimit":gateslimit}
    
    pickle.dump(DataDictionary, open( "savedata/lines_save.p", "wb" ) )
    
    # return limitStages
