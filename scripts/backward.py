#from numpy import array
from __future__ import division
def data(Param, fcf_backward, sol_vol, iteration, sol_lvl, stochastic):

    import pyomo.environ as pyomo
    from pyomo.opt import SolverFactory
    #from pyomo.util.timing import report_timing
    from pyomo.core import Suffix
    import copy
    import math
    from pyomo.opt.parallel import SolverManagerFactory
    from scripts.pyomo_model import obj_function
    from scripts.pyomo_model import load_balance
    from scripts.pyomo_model import energy_conservationB as energy_conservation
    from scripts.pyomo_model import storage_function, costtogo
    from scripts.pyomo_model import variables
    from utils.parameters import cutsback, pyomogates
    from utils.parameters import pyomoset, pyomohydro
    from utils import solver
    import progressbar
    import pickle
    #import timeit
    #from objbrowser import browse
    #from pyomo.util.timing import report_timing
    #report_timing()
    
    # parallelization
    if Param.parallel is False:
        from utils.solvermodule import backseq as solver_module
    else:
        from utils.solvermodule import backpar as solver_module

    # objective calculation
    if stochastic is True:
        if Param.commit > 0:
            from utils.objcalculation import objstrisk as obj_calc
        else:
            from utils.objcalculation import objst as obj_calc
    else:
        from utils.objcalculation import objdet as obj_calc

    # stimate progress
    bar = progressbar.ProgressBar(max_value = Param.stages*(iteration+1), \
    widgets=[progressbar.Bar('=', '[', ']'), 'Backward stage - iteration '+str(iteration+1)+' ',
             progressbar.Percentage()])
    bar.start()
    count = 0

    # import data
    dict_hydro = pickle.load(open("savedata/hydro_save.p", "rb"))
    dh_factor = dict_hydro['prodFactor']
    dh_limits = dict_hydro['u_limit']
    dict_batt = pickle.load(open("savedata/batt_save.p", "rb"))
    db_storage = dict_batt["b_storage"]
    dict_lines = pickle.load(open("savedata/lines_save.p", "rb"))
    dl_limits = dict_lines['l_limits']
    dict_wind = pickle.load(open("savedata/wind_hat_0.p", "rb"))
    dw_windhat = dict_wind['hat_area']
    dict_format = pickle.load(open("savedata/format_save.p", "rb"))
    df_demand = dict_format['demand']
    df_thmin = dict_format['thermalMin']
    df_thmax = dict_format['thermalMax']
    df_opcost = dict_format['opCost']
    dict_data = pickle.load(open("savedata/data_save_iter.p", "rb"))
    dd_rationing = dict_data['rationingData']
    dd_emissions = dict_data['emissionsData']
    b_storageData = dict_data['b_storageData']
    dict_wenergy = pickle.load(open("savedata/windspeed_save.p", "rb"))

    # data from dictionaries
    numBlocks = dict_format['numBlocks']
    numAreas = dict_data['numAreas']
    blocksdata = dict_data['blocksData']
    windPlants = dict_data['windPlants']
    thermalplants = dict_data['thermalPlants']
    smallplants = dict_data['smallPlants']
    hydroPlants = dict_data['hydroPlants']
    batteries = dict_data['batteries']
    volData = dict_data['volData']
    thermalData = dict_data['thermalData']
    #windData = dict_data['windData']
    smallData = dict_data['smallData']
    demandArea = dict_format['demandArea']
    RnwArea = dict_wenergy['RnwArea']
    
    circuits = dict_data['linesData']
    fcircuits = list(range(1, len(circuits)+1))
    
    # Define solver
    opt = solver.gurobi_solver(SolverFactory)
    #opt = solver.glpk_solver(SolverFactory)
    #opt = solver.cplex_solver(SolverFactory)
    #opt = solver.ipopt_solver(SolverFactory)
    #opt = solver.cbc_solver(SolverFactory)
    #opt = solver.xpress_solver(SolverFactory)
    
    # Define model
    model = pyomo.ConcreteModel()
    
    # SETS
    # set of demand blocks
    model.Blocks = pyomo.Set(initialize= list(range(1, numBlocks+1)))
    # set of state/cut
    #model.Cuts = pyomo.Set(initialize= [1])
    model.Cuts = pyomo.Set(initialize= list(range(1, iteration+2)))
    # set of hydroelectric plants / reservoirs / Chains
    model.Hydro = pyomo.Set(initialize= hydroPlants)
    # set of hydro plants with reservoirs
    setData = pyomohydro(hydroPlants, dict_data['hydroReservoir'])
    model.resHydro = pyomo.Set(initialize=setData)
    # generation chains: set of spill and turbining arcs
    setData = pyomoset(dict_hydro['S-downstream'])
    model.SpillArcs = pyomo.Set(initialize= setData, dimen=2)
    setData = pyomoset(dict_hydro['T-downstream'])
    model.TurbiningArcs = pyomo.Set(initialize= setData, dimen=2)
    # set of thermal plants
    model.Thermal = pyomo.Set(initialize= thermalplants)
    # set of small plants
    model.Small = pyomo.Set(initialize= smallplants)
    # set of wind farms
    model.Wind = pyomo.Set(initialize= windPlants)
    # set of battery units
    model.Batteries = pyomo.Set(initialize= batteries)
    # set of areas in the system
    model.Areas = pyomo.Set(initialize= list(range(1, numAreas+1)))
    model.AreasDmd = pyomo.Set(initialize= demandArea)
    model.AreasRnw = pyomo.Set(initialize= RnwArea)
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
            th_indx = thermalplants.index(i)
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
            sm_indx = smallplants.index(i)
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
    # production cost (CxC) for each hydro plant
    dictplant = {hydroPlants[z]: dict_hydro['oymcost'][z] for z in range(len(hydroPlants))}
    model.hydroCost = pyomo.Param(model.Hydro, initialize=dictplant)
    # production factor for each battery unit
    model.factorB = pyomo.Param(model.Batteries, mutable=True)
    # identification of batteries by areas
    dictplant = {batteries[z]: dict_batt['b_area'][z] for z in range(len(batteries))}
    model.BatteriesArea = pyomo.Param(model.Batteries, initialize=dictplant)
    # state volume by stage
    model.stateVol = pyomo.Param(model.Hydro, mutable=True)
    # state level of batteriy
    model.stateLvl = pyomo.Param(model.Batteries, mutable=True)
    model.stateLvlBlk = pyomo.Param(model.Batteries, model.Blocks, mutable=True)
    # coeficcient of lineal segments in the future cost function
    model.coefcTerm = pyomo.Param(model.Hydro, model.Cuts, mutable=True)
    # constant term of lineal segments in the future cost function
    model.constTerm = pyomo.Param(model.Cuts, mutable=True)
    # coeficcient of lineal segments in the future cost function
    model.coefcBatt = pyomo.Param(model.Batteries, model.Cuts, mutable=True)
    
    # BOUNDS
    # bounds (min and max) on hydro generation
    model.maxGenH = pyomo.Param(model.Hydro, model.Blocks, mutable=True)
    # bounds (min and max) on thermal generation
    model.minGenT = pyomo.Param(model.Thermal, model.Blocks, mutable=True)
    model.maxGenT = pyomo.Param(model.Thermal, model.Blocks, mutable=True)
    # bounds (min and max) on small generation
    model.minGenS = pyomo.Param(model.Small, model.Blocks, mutable=True)
    model.maxGenS = pyomo.Param(model.Small, model.Blocks, mutable=True)
    # bounds (min and max) on batteries generation
    model.maxGenB = pyomo.Param(model.Batteries, model.Blocks, mutable=True)
    # bounds (min and max) on wind area generation
    model.maxGenW = pyomo.Param(model.Areas, model.Blocks, mutable=True)
    # bounds (min and max) on capacity of reservoirs
    dictplant = {hydroPlants[z]: dict_hydro['volmin'][z] for z in range(len(hydroPlants))}
    model.minVolH = pyomo.Param(model.Hydro, initialize=dictplant)
    dictplant = {hydroPlants[z]: dict_hydro['volmax'][z] for z in range(len(hydroPlants))}
    model.maxVolH = pyomo.Param(model.Hydro, initialize=dictplant)
    # bounds (min and max) on capacity of batteries
    model.minlvlB = pyomo.Param(model.Batteries, mutable=True)
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
        
        # transmission network
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
        dictplant = {thermalplants[z]: (Param.thermal_co2[0]*thermalData[13][z])+
                     (Param.thermal_co2[1]*thermalData[12][z]*thermalData[11][z]) for z in range(len(thermalplants))}
        model.thermalFE = pyomo.Param(model.Thermal, initialize=dictplant)
        # emission factor for each small plant
        dictplant = {smallplants[z]: smallData[8][z] for z in range(len(smallplants))}
        model.smallFE = pyomo.Param(model.Small, initialize=dictplant)
        # emission factor for each wind power plant
        # dictplant = {windPlants[z]: windData[14][z] for z in range(len(windPlants))}
        # model.windFE = pyomo.Param(model.Areas, initialize=dictplant)
        # cost of CO2 emissions
        model.co2cost = pyomo.Param(mutable=True)
        
    ################### Optimization model ####################################
    
    # OBJ FUNCTION
    obj_function(Param, model, pyomo)
    
    # CONSTRAINTS
    # define constraint: demand must be served in each block and stage
    load_balance(Param, model, pyomo)
    
    # define constraint: energy conservation
    energy_conservation(model, pyomo)

    # define constraint: Wind production conservation
    storage_function(Param, model, pyomo)

    # define constraint: future cost funtion
    costtogo(Param, model, pyomo)
        
    # Creating instance
    model.dual = Suffix(direction=Suffix.IMPORT)
    #opt.set_instance(model)

    #################### Backward analysis ####################################

    int_conf = (1-Param.eps_risk)*Param.seriesBack
    int_bound = math.ceil(int_conf)

    # Loop analysis
    for i in range(Param.stages, 0, -1): # debug - stages

        # opf matrix restrictions
        for z in range(len(circuits)):
            for y in range(numBlocks):
                model.lineLimit[z+1, y+1] = dl_limits[i-1][circuits[z][0]-1][circuits[z][1]-1]*blocksdata[0][y]
        
        if Param.param_opf is True:
            # network modifications
            for z in range(len(circuits)):
                for area1 in range(numAreas):
                    model.flines[z+1, area1+1] = dict_intensity['matrixbeta'][i-1][z][area1]

        # flowgates constraints
        if Param.flow_gates is True:
            for gate1 in range(numGates):
                for y in range(numBlocks):
                    model.gateLimt[gate1+1, y+1] = gateslimit[gate1][i-1]*blocksdata[0][y]
        
        if Param.emissions is True:
            model.co2cost = dd_emissions[0][i-1]
            
        # update the local fcf
        #model.Cuts.clear()
        for z in range(iteration+1): #len(fcf_backward[i])):
            #model.Cuts.add(z+1)
            if i == Param.stages:
                model.constTerm[z+1] = fcf_backward[i][0][2]
                for y, plant in enumerate(batteries):
                    model.coefcBatt[plant, z+1] = fcf_backward[i][0][1][y]
                for y, plant in enumerate(hydroPlants):
                    model.coefcTerm[plant, z+1] = fcf_backward[i][0][0][y]
            else:
                model.constTerm[z+1] = fcf_backward[i][z][2]
                for y, plant in enumerate(batteries):
                    model.coefcBatt[plant, z+1] = fcf_backward[i][z][1][y]
                for y, plant in enumerate(hydroPlants):
                    model.coefcTerm[plant, z+1] = fcf_backward[i][z][0][y]
            
        #model.ctFcf.reconstruct()

        # update rationing cost and demand values by stage
        for area1 in range(numAreas):
            model.rationing[area1+1] = dd_rationing[area1][i-1]
            for y in range(numBlocks):
                model.demand[area1+1, y+1] = df_demand[area1][i-1][y]
                model.maxGenW[area1+1, y+1] = dw_windhat[area1][i-1]*blocksdata[0][y]
            
        # define cuts for states simulation
        cuts_iter, cuts_iter_B = cutsback(i, dict_data, sol_vol, iteration, sol_lvl, db_storage)

        for z, plant in enumerate(hydroPlants):
            model.factorH[plant] = dh_factor[z][i-1]
            for y in range(numBlocks):
                model.maxGenH[plant, y+1] = dh_limits[z][i-1]*blocksdata[0][y]

        for z, plant in enumerate(batteries):
            model.minlvlB[plant] = db_storage[z][i-1][1]
            model.maxlvlB[plant] = db_storage[z][i-1][0]
            model.factorB[plant] = dict_data['battData'][4][z]
            for y in range(numBlocks):
                model.maxGenB[plant, y+1] = dict_batt["b_limit"][z][i-1]*blocksdata[0][y]*b_storageData[z][y] # restrictions

        # update thermal generation cost by stage
        for z, plant in enumerate(thermalplants):
            model.cost[plant] = df_opcost[z][i-1]
            for y in range(numBlocks):
                model.minGenT[plant, y+1] = df_thmin[i-1][z]*blocksdata[0][y]
                model.maxGenT[plant, y+1] = df_thmax[i-1][z]*blocksdata[0][y]

        for z, plant in enumerate(smallplants):
            for y in range(numBlocks):
                model.minGenS[plant, y+1] = 0
                model.maxGenS[plant, y+1] = dict_format['smallMax'][i-1][z]*blocksdata[0][y]
        
        # loop - hyperplanes
        feasible_cuts = []
        for j in range(len(cuts_iter[0])):

            # initial condition for coefficient phi and constant delta
            phi_delta = [[0]*len(hydroPlants), [0]*len(batteries), 0]

            for z, plant in enumerate(hydroPlants):
                model.stateVol[plant] = cuts_iter[z][j]
            for z, plant in enumerate(batteries):
                model.stateLvl[plant] = cuts_iter_B[z][j]
                for y in range(numBlocks):
                    model.stateLvlBlk[plant,y+1] = cuts_iter_B[z][j]/numBlocks
            
            # Solver module (Single core or parallel)
            objective_list, duals_batt, duals, total_obj = solver_module(Param, i,dict_data,
            dict_format,model,opt,SolverFactory,SolverManagerFactory,dict_wenergy)
            
            # progress analysis
            bar.update(count+1); count += 1
            #print(total_obj)
            
            delta_cut, phi_risk, phi_batt_risk = obj_calc(objective_list,int_bound,Param.seriesBack,
            Param.commit,Param.eps_risk,hydroPlants,batteries,duals,duals_batt,total_obj)

            # save phi and delta for the future cost function
            delta_cut_2 = sum([phi_risk[p]*cuts_iter[p][j] for p in range(len(phi_risk))])
            delta_cut_2_batt = sum([phi_batt_risk[p]*cuts_iter_B[p][j] for p in range(len(phi_batt_risk))])
            # Results for next iteration
            delta = delta_cut - delta_cut_2_batt - delta_cut_2
            #print(delta)

            # last phi_delta
            for z in range(len(hydroPlants)): phi_delta[0][z] = phi_risk[z]
            for z in range(len(batteries)): phi_delta[1][z] = phi_batt_risk[z]
            phi_delta[2] = delta

            feasible_cuts.append(phi_delta)

        #######################################################################

        fcf_backward[i-1]=copy.deepcopy(feasible_cuts)
        
        datafcf = {"fcf_backward":fcf_backward}
        pickle.dump(datafcf, open("savedata/fcfdataIter.p", "wb"))
    
