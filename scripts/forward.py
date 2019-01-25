# forward stage
from __future__ import division
def data(confidence, Param, iteration, fcf_Operator): 

    #import InputFilesForw
    import pyomo.environ as pyomo
    from pyomo.opt import SolverFactory
    from pyomo.core import Suffix
    from utils.parameters import pyomoset, pyomohydro, pyomogates
    from scripts.pyomo_model import obj_function
    from scripts.pyomo_model import load_balance
    from scripts.pyomo_model import energy_conservationF as energy_conservation
    from scripts.pyomo_model import storage_function, costtogo
    from scripts.pyomo_model import variables
    from utils.saveresults import saveiter
    from utils import solver
    import progressbar
    import pickle

    # Cost-to-go function
    if fcf_Operator is True:
        dict_fcf = pickle.load(open("savedata/fcfdataIter.p", "rb"))
    else:
        dict_fcf = pickle.load(open("savedata/fcfdata.p", "rb"))
    fcf_backward = dict_fcf['fcf_backward']
        
    # progress analysis
    bar = progressbar.ProgressBar(max_value = Param.seriesForw*Param.stages, \
    widgets=[progressbar.Bar('=', '[', ']'), ' Forward stage - iteration '+str(iteration+1)+' ', 
             progressbar.Percentage()])
    bar.start(); count = 0
    
    # import data
    dict_hydro = pickle.load(open("savedata/hydro_save.p", "rb"))
    dh_factor = dict_hydro['prodFactor']
    dh_limits = dict_hydro['u_limit']
    dict_batt = pickle.load(open("savedata/batt_save.p", "rb"))
    dict_lines = pickle.load(open("savedata/lines_save.p", "rb"))
    dict_windenergy = pickle.load(open("savedata/windspeed_save.p", "rb"))
    dict_wind = pickle.load(open("savedata/wind_hat_0.p", "rb"))
    dict_format = pickle.load(open("savedata/format_save.p", "rb"))
    df_demand = dict_format['demand']
    df_thmin = dict_format['thermalMin']
    df_thmax = dict_format['thermalMax']
    df_opcost = dict_format['opCost']
    dict_data = pickle.load(open("savedata/data_save_iter.p", "rb"))
    dd_rationing = dict_data['rationingData']
    dd_emissions = dict_data['emissionsData']
    b_storageData = dict_data['b_storageData']

    # data from dictionaries
    numAreas = dict_data['numAreas']
    numBlocks = dict_format['numBlocks']
    blocksData = dict_data['blocksData']
    thermalPlants = dict_data['thermalPlants']
    smallData = dict_data['smallData']
    smallPlants = dict_data['smallPlants']
    batteries = dict_data['batteries']
    hydroPlants = dict_data['hydroPlants']
    volData = dict_data['volData']
    thermalData = dict_data['thermalData']
    demandArea = dict_format['demandArea']
    rnwArea = dict_windenergy['RnwArea']
    
    circuits = dict_data['linesData']
    fcircuits = list(range(1, len(circuits)+1))

    # print results
    lenblk = range(numBlocks)
    lenstg = range(Param.stages); lensc = range(Param.seriesForw)

    genThermal = [[[[[] for bl in lenblk] for z in thermalPlants] for x in lenstg] for y in lensc]
    genSmall = [[[[[] for bl in lenblk] for z in smallPlants] for x in lenstg] for y in lensc]
    genHydro = [[[[[] for bl in lenblk] for z in hydroPlants] for x in lenstg] for y in lensc]
    genwind = [[[[[] for bl in lenblk] for z in range(numAreas)] for x in lenstg] for y in lensc]
    spillwind = [[[[[] for bl in lenblk] for z in range(numAreas)] for x in lenstg] for y in lensc]
    genBatteries = [[[[[] for bl in lenblk] for z in batteries] for x in lenstg] for y in lensc]
    genDeficit = [[[[[] for bl in lenblk] for x in lenstg] for y in lensc] for x in range(numAreas)]
    emissCurve = [[[[] for bl in lenblk] for x in lenstg] for y in lensc]
    loadBatteries = [[[[[] for bl in lenblk] for z in batteries] for x in lenstg] for y in lensc]
    lvlBatteries = [[[[] for z in batteries] for x in lenstg] for y in lensc]
    lvlHydro = [[[[] for z in hydroPlants] for x in lenstg] for y in lensc]
    spillHydro = [[[[[] for bl in lenblk] for z in hydroPlants] for x in lenstg] for y in lensc]
    linTransfer = [[[[[] for a in range(numAreas)] for z in range(numAreas)] for x in lenstg] for y in lensc]
    genRnws = [[[[[] for bl in lenblk] for z in range(numAreas)] for x in lenstg] for y in lensc]
    
    # Define solver
    opt = solver.gurobi_solver(SolverFactory)
    #opt = solver.glpk_solver(SolverFactory)
    #opt = solver.cplex_solver(SolverFactory)
    #opt = solver.ipopt_solver(SolverFactory)
    #opt = solver.cbc_solver(SolverFactory)
    #opt = solver.xpress_solver(SolverFactory)
    
        # Define abstract model
    model = pyomo.ConcreteModel()

    # SETS
    # set of demand blocks
    model.Blocks = pyomo.Set(initialize=list(range(1, numBlocks+1)))
    # set of state/cut
    model.Cuts = pyomo.Set(initialize= list(range(1, iteration+2)))
    #model.Cuts = pyomo.Set(initialize=[1])
    # set of hydroelectric plants / reservoirs
    model.Hydro = pyomo.Set(initialize=hydroPlants)
    # set of hydro plants with reservoirs
    setData = pyomohydro(hydroPlants, dict_data['hydroReservoir'])
    model.resHydro = pyomo.Set(initialize=setData)
    # generation chains: set of spill and turbining arcs
    setData = pyomoset(dict_hydro['S-downstream'])
    model.SpillArcs = pyomo.Set(initialize= setData, dimen=2)
    setData = pyomoset(dict_hydro['T-downstream'])
    model.TurbiningArcs = pyomo.Set(initialize= setData, dimen=2)
    # set of thermal plants
    model.Thermal = pyomo.Set(initialize=thermalPlants)
    # set of thermal plants
    model.Small = pyomo.Set(initialize=smallPlants)
    # set of wind farms
    model.Wind = pyomo.Set(initialize=dict_data['windPlants'])
    # set of battery units
    model.Batteries = pyomo.Set(initialize=batteries)
    # set of areas in the system
    model.Areas = pyomo.Set(initialize=list(range(1, numAreas+1)))
    model.AreasDmd = pyomo.Set(initialize= demandArea)
    model.AreasRnw = pyomo.Set(initialize= rnwArea)
    # set of lines in the system
    model.Circuits = pyomo.Set(initialize= fcircuits)
    
    # Plants by areas
    def In_init(model, area):
        retval = [];
        for lines_def in range(len(circuits)):
            lines_area = circuits[lines_def][0]
            if lines_area == area:
                retval.append(lines_def+1)
        return retval
    model.linesAreaIn = pyomo.Set(model.Areas, initialize= In_init)
    def Out_init(model, area):
        retval = [];
        for lines_def in range(len(circuits)):
            lines_area = circuits[lines_def][1]
            if lines_area == area:
                retval.append(lines_def+1)
        return retval
    model.linesAreaOut = pyomo.Set(model.Areas, initialize= Out_init)
    
    def thermalArea_init(model, area):
        retval = []
        for i in model.Thermal:
            th_indx = thermalPlants.index(i)
            are_pl = dict_format['area_thermal'][th_indx]
            if are_pl == area:
                retval.append(i)
        return retval
    model.ThermalArea = pyomo.Set(model.Areas, initialize= thermalArea_init)
    
    def hydroArea_init(model, area):
        retval = []
        for i in model.Hydro:
            hy_indx = hydroPlants.index(i)
            are_pl = dict_format['area_hydro'][hy_indx]
            if are_pl == area:
                retval.append(i)
        return retval
    model.HydroArea = pyomo.Set(model.Areas, initialize= hydroArea_init)
    
    def smallArea_init(model, area):
        retval = []
        for i in model.Small:
            sm_indx = smallPlants.index(i)
            are_pl = dict_format['area_small'][sm_indx]
            if are_pl == area:
                retval.append(i)
        return retval
    model.SmallArea = pyomo.Set(model.Areas, initialize= smallArea_init)
    
    # PARAMETERS
    # cost of thermal production
    model.cost = pyomo.Param(model.Thermal, mutable=True)
    # cost of energy rationing
    model.rationing = pyomo.Param(model.Areas, mutable=True)
    # demand for each stage
    model.demand = pyomo.Param(model.Areas, model.Blocks, mutable=True)
    # inflows for each stage
    model.inflows = pyomo.Param(model.Hydro, mutable=True)
    # wind inflows for each stage
    model.meanWind = pyomo.Param(model.Areas, model.Blocks, mutable=True)
    # production factor for each hydro plant
    model.factorH = pyomo.Param(model.Hydro, mutable=True)
    # Hydro plants by area
    # production cost (CxC) for each hydro plant
    dictplant = {hydroPlants[z]: dict_hydro['oymcost'][z] for z in range(len(hydroPlants))}
    model.hydroCost = pyomo.Param(model.Hydro, initialize=dictplant)
    # production factor for each battery unit
    model.factorB = pyomo.Param(model.Batteries, mutable=True)
    # Batteries by area
    dictplant = {batteries[z]: dict_batt['b_area'][z] for z in range(len(batteries))}
    model.BatteriesArea = pyomo.Param(model.Batteries, initialize=dictplant)
    # coeficcient of lineal segments in the future cost function
    model.coefcTerm = pyomo.Param(model.Hydro, model.Cuts, mutable=True)
    # constant term of lineal segments in the future cost function
    model.constTerm = pyomo.Param(model.Cuts, mutable=True)
    # coeficcient of lineal segments in the future cost function
    model.coefcBatt = pyomo.Param(model.Batteries, model.Cuts, mutable=True)
    # Initial volume in reservoirs
    model.iniVol = pyomo.Param(model.Hydro, mutable=True)
    # Initial storage in batteries
    model.iniLvl = pyomo.Param(model.Batteries, mutable=True)
    model.iniLvlBlk = pyomo.Param(model.Batteries, model.Blocks, mutable=True)

    # BOUNDS
    # bounds (min and max) on hydro generation
    #model.minGenH = pyomo.Param(model.Hydro, model.Blocks, mutable=True)
    model.maxGenH = pyomo.Param(model.Hydro, model.Blocks, mutable=True)
    # bounds (min and max) on thermal generation
    model.minGenT = pyomo.Param(model.Thermal, model.Blocks, mutable=True)
    model.maxGenT = pyomo.Param(model.Thermal, model.Blocks, mutable=True)
    # bounds (min and max) on thermal generation
    model.minGenS = pyomo.Param(model.Small, model.Blocks, mutable=True)
    model.maxGenS = pyomo.Param(model.Small, model.Blocks, mutable=True)
    # bounds (min and max) on batteries generation
    #model.minGenB = pyomo.Param(model.Batteries, model.Blocks, mutable=True)
    model.maxGenB = pyomo.Param(model.Batteries, model.Blocks, mutable=True)
    # bounds (min and max) on wind area generation
    model.maxGenW = pyomo.Param(model.Areas, model.Blocks, mutable=True)
    # bounds (min and max) on capacity of reservoirs
    dictplant = {hydroPlants[z]: dict_hydro['volmin'][z] for z in range(len(hydroPlants))}
    model.minVolH = pyomo.Param(model.Hydro, initialize=dictplant)
    dictplant = {hydroPlants[z]: dict_hydro['volmax'][z] for z in range(len(hydroPlants))}
    model.maxVolH = pyomo.Param(model.Hydro, initialize=dictplant)
    # bounds (min and max) on capacity of batteries
    model.maxlvl = pyomo.Param(model.Batteries, mutable=True)
    model.maxlvlB = pyomo.Param(model.Batteries, mutable=True)
    # bounds (max) on capacity of lines
    model.lineLimit = pyomo.Param(model.Circuits, model.Blocks, mutable=True)
    
    ###########################################################################
    
    # Bounds and DECISION VARIABLES
    variables(model, pyomo)
    
    ###########################################################################
    
    # conditional constraints
    
    if Param.dist_free is True:
        
        dict_pleps = pickle.load(open("savedata/pleps_save.p", "rb"))
        residual = dict_pleps['p_points']
        
        numPleps = dict_pleps['plepcount']
        model.plepNum = pyomo.Set(initialize= list(range(1, numPleps+1)))
        
        # coeficient pleps variables
        model.factorPlep = pyomo.Var(model.Areas, model.Blocks, model.plepNum, domain=pyomo.NonNegativeReals)
        # aggregated renewables production
        model.RnwLoad = pyomo.Var(model.Areas, model.Blocks)
        
        # p_efficient points
        model.plep = pyomo.Param(model.Areas, model.Blocks, model.plepNum, mutable=True)
        
    if Param.param_opf is True:
        dict_intensity = pickle.load(open("savedata/matrixbeta_save.p", "rb"))
        
        # generation chains: set of spill and turbining arcs
        setData = pyomoset(dict_intensity['matrixLineBus'][0])
        model.linebus = pyomo.Set(initialize= setData, dimen=2)
        
        # lines intensities OPF
        model.flines = pyomo.Param(model.Circuits, model.Areas, mutable=True)
        
    # flowgates parameters
    if Param.flow_gates is True:
        
        numGates = dict_format['numGates']
        gatesets = dict_lines['gatesets']
        gateslimit = dict_lines['gateslimit']
    
        # set of gates flow in the system
        model.Gates = pyomo.Set(initialize= list(range(1, numGates+1)))
    
        # flow gates set
        setData = pyomogates(gatesets)
        model.gateLines = pyomo.Set(initialize=setData, dimen=3)
    
        # defining limit of gate flows
        model.gateLimt = pyomo.Param(model.Gates, model.Blocks, mutable=True)
    
    # emissions consideration
    if Param.emissions is True:
        
        # emission factor for each hydro plant
        dictplant = {hydroPlants[z]: volData[15][z] for z in range(len(hydroPlants))}
        model.hydroFE = pyomo.Param(model.Hydro, initialize=dictplant)
        # emission factor for each thermal plant
        dictplant = {thermalPlants[z]: (Param.thermal_co2[0]*thermalData[13][z])+
                     (Param.thermal_co2[1]*thermalData[12][z]*thermalData[11][z]) for z in range(len(thermalPlants))}
        model.thermalFE = pyomo.Param(model.Thermal, initialize=dictplant)
        # emission factor for each small plant
        dictplant = {smallPlants[z]: smallData[8][z] for z in range(len(smallPlants))}
        model.smallFE = pyomo.Param(model.Small, initialize=dictplant)
        # cost of CO2 emissions
        model.co2cost = pyomo.Param(mutable=True)
        
    ################### Optimization model ####################################
    
    # OBJ FUNCTION
    obj_function(Param, model, pyomo)
    
    # CONSTRAINTS
    # define constraint: demand must be served in each block and stage
    load_balance(Param, model, pyomo)
    
    # define constraint: energy conservation
    energy_conservation(Param, model, pyomo)

    # define constraint: Wind production conservation
    storage_function(Param, model, pyomo)

    # define constraint: future cost funtion
    costtogo(Param, model, pyomo)

    # Creating instance
    model.dual = Suffix(direction=Suffix.IMPORT)

    ################ Forward analysis #############################

    sol_cost_scn = [[],[],[]] # Save operation csot and cost-to-go value

    # Save results
    sol_vol_iter = [[0 for x in hydroPlants] for x in lenstg] # Hydro iteration
    sol_lvl_batt = [[0 for x in batteries] for x in lenstg] # Batteries iteration

    # Save new state for the current iteration
    sol_scn = [[] for x in lensc] # Hydro iteration
    marg_costs = [[[] for x in lenstg] for x in lensc] # Hydro iteration

    # Create a model instance and optimize
    for k in lensc: # Iteration by scenarios

        # Update the initial volume at each stage
        for i, plant in enumerate(hydroPlants): 
            model.iniVol[plant] = dict_data['volData'][0][i]
        for i, plant in enumerate(batteries): 
            model.iniLvl[plant] = dict_data['battData'][0][i]*dict_batt["b_storage"][i][0][0]
            for y in lenblk:
                model.iniLvlBlk[plant, y+1] = dict_data['battData'][0][i]*dict_batt["b_storage"][i][0][0]/numBlocks

        sol_cost = [[],[],[]] # Save operation cost and cost-to-go value

        for s in lenstg: # Iteration by stages

            for z in range(len(circuits)):
                for y in lenblk:
                    model.lineLimit[z+1, y+1] = dict_lines['l_limits'][s][circuits[z][0]-1][circuits[z][1]-1]*blocksData[0][y]
            
            # opf matriz restrictions
            if Param.param_opf is True:
                for z in range(len(circuits)):
                    for area1 in range(numAreas):
                        model.flines[z+1,area1+1]= dict_intensity['matrixbeta'][s][z][area1]
            # flowgates constraints
            if Param.flow_gates is True:
                for gate1 in range(numGates):
                    for y in lenblk:
                        model.gateLimt[gate1+1, y+1] = gateslimit[gate1][s]*blocksData[0][y]

            InflowsHydro = []
            InflowsHydro += [dict_format['inflow_hydro'][n][1][s][k] for n in range(len(hydroPlants))]

            for z, plant in enumerate(hydroPlants):
                model.factorH[plant] = dh_factor[z][s]
                model.inflows[plant] = InflowsHydro[z]
                for y in lenblk:
                    model.maxGenH[plant, y+1] = dh_limits[z][s]*blocksData[0][y]
            
            if Param.emissions is True:
                model.co2cost = dd_emissions[0][s]
            
            for y in range(numAreas):
                model.rationing[y+1] = dd_rationing[y][s]
            
            
            if Param.dist_free is True:
                # update rationing cost and demand values by stage
                for area1 in range(numAreas):
                    for y in lenblk:
                        for plp in range(numPleps):
                            model.plep[area1+1, y+1, plp+1] = residual[s][k][area1][y][plp]
            else:
                # wind energy
                for z in lenblk:
                    for y in range(numAreas):
                        model.meanWind[y+1,z+1] = dict_windenergy['windenergy_area'][y][s][k][z]

            for z in lenblk:
                for y in range(numAreas):
                    model.demand[y+1,z+1] = df_demand[y][s][z]
                    model.maxGenW[y+1,z+1] = dict_wind['hat_area'][y][s]*blocksData[0][z]
                        
            # Update the generation cost
            for i, plant in enumerate(thermalPlants):
                model.cost[plant] = df_opcost[i][s]
                for y in lenblk:
                    model.minGenT[plant, y+1] = df_thmin[s][i]*blocksData[0][y]
                    model.maxGenT[plant, y+1] = df_thmax[s][i]*blocksData[0][y]

            # Update small plants limits
            for i, plant in enumerate(smallPlants):
                for y in lenblk:
                    model.minGenS[plant, y+1] = 0
                    model.maxGenS[plant, y+1] = dict_format['smallMax'][s][i]*blocksData[0][y]

            # Update batteries limits
            for i, plant in enumerate(batteries):
                model.maxlvl[plant] = dict_batt["b_storage"][i][s][1]
                model.maxlvlB[plant] = dict_batt["b_storage"][i][s][0]*blocksData[0][y]*b_storageData[i][y]
                model.factorB[plant] = dict_data['battData'][4][i]
                for y in lenblk:
                    model.maxGenB[plant, y+1] = dict_batt['b_limit'][i][s]*blocksData[0][y]*b_storageData[i][y] # restrictions

            # Update the cost-to-go function
            #model.Cuts.clear()
            for z in range(iteration+1): # len(fcf_backward[s+1])):
                #model.Cuts.add(z+1)
                if s+1 == Param.stages:
                    model.constTerm[z+1] = fcf_backward[s+1][0][2]
                    for y, plant in enumerate(batteries):
                        model.coefcBatt[plant, z+1] = fcf_backward[s+1][0][1][y]
                    for y, plant in enumerate(hydroPlants):
                        model.coefcTerm[plant, z+1] = fcf_backward[s+1][0][0][y]
                else:
                    model.constTerm[z+1] = fcf_backward[s+1][z][2]
                    for y, plant in enumerate(batteries):
                        model.coefcBatt[plant, z+1] = fcf_backward[s+1][z][1][y]
                    for y, plant in enumerate(hydroPlants):
                        model.coefcTerm[plant, z+1] = fcf_backward[s+1][z][0][y]
            #model.ctFcf.reconstruct()

            # solver
            opt.solve(model)#, symbolic_solver_labels=False) #, tee=True)
            #with open('pyomo_model.txt', 'w') as f:
            #    model.pprint(ostream=f)
            # instance.display()

            # objective function value
            sol_objective = model.OBJ(); costtogo = model.futureCost()
            sol_cost[0].append(sol_objective-costtogo); sol_cost[1].append(sol_objective)
            sol_scn[k].append(sol_objective-costtogo)
            #print(sol_objective)

            vol_f_stage = [] # Save results of initial volume - v_t+1
            for vol_fin in [model.vol]:
                varobject = getattr(model, str(vol_fin))
                vol_f_stage += [varobject[i].value for i in hydroPlants]

            lvl_f_stage = [] # Save results of initial level - l_t+1
            for lvl_fin in [model.lvl]:
                varobject = getattr(model, str(lvl_fin))
                lvl_f_stage += [varobject[i].value for i in batteries]

            # Svael volt_t+1 for the next backward iteration
            sol_vol_iter[s] = [sum(x) for x in zip(sol_vol_iter[s], vol_f_stage)]
            sol_lvl_batt[s] = [sum(x) for x in zip(sol_lvl_batt[s], lvl_f_stage )]

            # Update the initial volume at each stage
            for i, plant in enumerate(hydroPlants):
                model.iniVol[plant] = vol_f_stage[i]
            for i, plant in enumerate(batteries): 
                model.iniLvl[plant] = lvl_f_stage[i]
                for y in lenblk:
                    model.iniLvlBlk[plant,y+1] = lvl_f_stage[i]/numBlocks

            # marginal cost of each area
            if (iteration + 1 == Param.max_iter or confidence == 1):
                duals_dmd = [[[] for x in lenblk] for y in range(numAreas)]
                d_object = getattr(model, 'ctDemand')
                for areadem in range(numAreas):
                    for i in lenblk:
                        duals_dmd[areadem][i].append(model.dual[d_object[areadem+1,i+1]])
                marg_costs[k][s] = duals_dmd

            # RESULTS
            if ((iteration + 1 == Param.max_iter or confidence == 1) and Param.results is True):

                (genThermal,genHydro,genBatteries,genDeficit,loadBatteries,lvlBatteries,
                lvlHydro,linTransfer,spillHydro,genwind,spillwind,genSmall,emsscurve,genRnws) = saveiter(k,
                s,lenblk,thermalPlants,model,genThermal,hydroPlants,batteries,genHydro,
                genBatteries,loadBatteries,lvlBatteries,lvlHydro,genDeficit,numAreas,
                linTransfer,circuits,spillHydro,genwind,spillwind,genSmall,smallPlants,
                rnwArea,Param,emissCurve,genRnws)

            # progress of the analysis
            bar.update(count+1)
            count += 1

        # Operation costs by scenarios
        sol_cost_scn[0].append(sum(sol_cost[0]))
        sol_cost_scn[1].append(sol_cost[1][0])
        sol_cost_scn[2].append(sum(sol_cost[0][:(Param.stages-Param.bnd_stages)]))

#    for s in lenstg:
#        # save the last solutions
#        last_sol = [x/dataParam.sf for x in sol_vol_iter[s]]
#        last_batt = [x/dataParam.sf for x in sol_lvl_batt[s]]
#        if last_sol not in sol_vol[s+1] or last_batt not in sol_lvl[s+1]:
#            sol_vol[s+1].append([x/dataParam.sf for x in sol_vol_iter[s]])
#            sol_lvl[s+1].append([x/dataParam.sf for x in sol_lvl_batt[s]])

    # Export results
    if ((iteration + 1 == Param.max_iter or confidence == 1) and Param.results is True):

        # export data
        DataDictionary = { "genThermal":genThermal,"genHydro":genHydro,"genSmall":genSmall,
        "genBatteries":genBatteries,"genDeficit":genDeficit,"loadBatteries":loadBatteries,
        "lvlBatteries":lvlBatteries,"lvlHydro":lvlHydro,"linTransfer":linTransfer,
        "spillHydro":spillHydro,"genwind":genwind,"spillwind":spillwind,"marg_costs":marg_costs,
        "emsscurve":emsscurve,"genRnws":genRnws}

        pickle.dump(DataDictionary, open( "savedata/results_save.p", "wb" ) )

    return (sol_vol_iter, sol_lvl_batt, sol_cost_scn, sol_scn)

