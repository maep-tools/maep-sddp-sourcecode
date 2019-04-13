
def pyomobuses(param,val):

    """
    Function that flattens the multidimensional dispaset input data into the pyomo format:
    a dictionnary with a tuple and the parameter value.
    The tuple contains the strings of the corresponding set values
    """
    param_new = set()
    if val == 'in':
        for k in range(len(param)):
            param_new.add((k+1, param[k][0]))
    if val == 'out':
        for k in range(len(param)):
            param_new.add((k+1, param[k][1]))
    return param_new

#def pyomobuses2(param,val):
#
#    """
#    Function that flattens the multidimensional dispaset input data into the pyomo format:
#    a dictionnary with a tuple and the parameter value.
#    The tuple contains the strings of the corresponding set values
#    """
#    param_new = set()
#    if val == 'in':
#        for k in range(len(param)):
#            param_new.add(param[k][0])
#    if val == 'out':
#        for k in range(len(param)):
#            param_new.add(param[k][1])
#    return param_new

###############################################################################

def pyomoset(param):

    """
    Function that flattens the multidimensional dispaset input data into the pyomo format:
    a dictionnary with a tuple and the parameter value.
    The tuple contains the strings of the corresponding set values
    """
    param_new = set()
    for k in range(len(param)):
        param_new.add((param[k][0], param[k][1]))

    return param_new

###############################################################################
    
def pyomohydro(set1, set2):

    """
    Function that flattens the multidimensional dispaset input data into the pyomo format:
    a dictionnary with a tuple and the parameter value.
    The tuple contains the strings of the corresponding set values
    """
    param_new = set()
    for k in range(len(set1)):
        if set2[k] == 1:
            param_new.add((set1[k]))

    return param_new

###############################################################################
    
def pyomogates(param):
    
    param_new = set()
    for k in range(len(param)):
        param_new.add((param[k][0], param[k][1], param[k][2]))

#    param_new = {}; data = 0
#    for k in set3:
#        for z in set1:
#            for y in set2:
#                param_new[(k, z, y)] = param[data]
#                data = data + 1

    return param_new

###############################################################################

def cutsback(stage,dict_data,sol_vol,iteration,sol_lvl,db_storage):

    hydroPlants = dict_data['hydroPlants']
    batteries = dict_data['batteries']
    battData = dict_data['battData']
    volData = dict_data['volData']

    # calculate the volume states
    if stage == 1:
        # initial conditiona
        cuts_reservoirs = []
        for m in range(len(hydroPlants)): # Loop for all hydro plants
            vol_cut = [volData[0][m]]
            cuts_reservoirs.append(vol_cut)
    else:
        # empty reservoirs
        cuts_reservoirs = []
        for m in range(len(hydroPlants)): # Loop for all hydro plants
            vol_cut = [volData[1][m]]
            cuts_reservoirs.append(vol_cut)

    # calculate the storage cuts
    cuts_storage = []
    for m in range(len(batteries)): # Loop for all batteries
        lvl_cut = [db_storage[m][stage-1][1]*battData[1][m]]
        cuts_storage.append(lvl_cut)

    if iteration ==0:

        # Hydro plants
        cuts_iter_stage = []
        cuts_iter_stage.extend(cuts_reservoirs)
        # Batteries
        cuts_iter_stage_B = []
        cuts_iter_stage_B.extend(cuts_storage)

    else:

        # HYDRO - Results from last iteration
        cuts_iter_stage = [[] for x in range(len(hydroPlants))]
        # Loop for include vol_fin from the last iteration
        for c in range(len(hydroPlants)):
            cuts_iter_stage[c] = list(cuts_reservoirs[c])
        for c in range(len(hydroPlants)):
            for k in range(len(sol_vol[stage-1])):
                cuts_iter_stage[c].append(sol_vol[stage-1][k][c])
                # aux_vec = cuts_iter_stage[c]; print(aux_vec)

        # storage results
        cuts_iter_stage_B = [[] for x in range(len(batteries))]
        # Loop for include lvl_fin from the last iteration
        for c in range(len(batteries)):
            cuts_iter_stage_B[c] = list(cuts_storage[c])
        for c in range(len(batteries)):
            for k in range(len(sol_lvl[stage-1])):
                cuts_iter_stage_B[c].append(sol_lvl[stage-1][k][c])

    return cuts_iter_stage,cuts_iter_stage_B
