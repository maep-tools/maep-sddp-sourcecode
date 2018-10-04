
import sys

def paramlimits(Param):
    
    import pickle
    
    # Load the dictionary back from the pickle file
    dict_data = pickle.load(open("savedata/data_save.p", "rb"))
    # No of maximum number of stages
    noStages = len(dict_data['horizon'])
    
    noBlocks = len(dict_data['blocksData'][0])
    if len(dict_data['indicesData']) > 1:
        noIndices = len(dict_data['indicesData'][0])-1
        if noIndices != (noBlocks*12):
            sys.exit('Wind speed indices do not correspond to the format ('+str(noBlocks*12)+' indices defined vs '+str(noIndices)+' indices input )')
    
    if Param.stages > noStages:
        sys.exit('Number of stages exceeds the maximum number allowed by the data of the system ('+str(noStages)+' stages)')

def valmodel(Param):
    
    if Param.wind_freeD is True and Param.wind_model2 is True:
        sys.exit('The parameters (Class Parameters) "wind_freeD" and "wind_model2" are True at the same time. You need to choose one model.')

    if Param.flow_gates is True or Param.parallel is True or Param.wind_model2 is True:
        sys.exit('The parameters (Class Parameters) "parallel", "wind_model2" or "flow_gates" refers to inconclusive implementations. Please set they as "False".')

def areavalidation(area,substring):
    
    sys.exit('Area or node "' +str(area) + '" does not exist or it is inactive - sheet '+substring)
