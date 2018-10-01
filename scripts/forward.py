# forward stage
from __future__ import division
def data(confidence, Param, iteration, fcf_Operator): 

    #import InputFilesForw
    import pyomo.environ as pyomo
    from pyomo.opt import SolverFactory
    from pyomo.core import Suffix
    from utils.parameters import pyomoset, pyomohydro, pyomogates
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
    model.minlvlB = pyomo.Param(model.Batteries, mutable=True)
    model.maxlvlB = pyomo.Param(model.Batteries, mutable=True)
    # bounds (max) on capacity of lines
    model.lineLimit = pyomo.Param(model.Circuits, model.Blocks, mutable=True)

    # reservoirs limits
    def boundVolH(model, h):
        return (model.minVolH[h], model.maxVolH[h])
    # batteries storage limits
    def boundlvlB(model, r):
        return (model.minlvlB[r], model.maxlvlB[r])
    def boundlvlBlock(model, r, b):
        return (0, model.maxlvlB[r])
    # thermal production
    def boundProdT(model, t, b):
        return (model.minGenT[t, b], model.maxGenT[t, b])
    # small production
    def boundProdS(model, m, b):
        return (model.minGenS[m, b], model.maxGenS[m, b])
    # hydro production
    def boundProdH(model, h, b):
        return (0, model.maxGenH[h, b])
    # batteries production
    def boundProdB(model, r, b):
        return (0, model.maxGenB[r, b])
    # wind area production
    def boundProdW(model, a, b):
        return (0, model.maxGenW[a, b])
    # lines limits
    def boundLines(model, l, b):
        return (0, model.lineLimit[l, b])
    # lines limits
    def boundDeficit(model, a, b):
        return (0, model.demand[a, b])
    
    # DECISION VARIABLES
    # thermal production
    model.prodT = pyomo.Var(model.Thermal, model.Blocks, bounds=boundProdT)
    # small production
    model.prodS = pyomo.Var(model.Small, model.Blocks, bounds=boundProdS)
    # hydro production
    model.prodH = pyomo.Var(model.Hydro, model.Blocks, bounds=boundProdH)
    # wind power production
    model.prodW = pyomo.Var(model.AreasRnw, model.Blocks, bounds=boundProdW)
    # Battery production
    model.prodB = pyomo.Var(model.Batteries, model.Blocks, bounds=boundProdB)
    # battery charge
    model.chargeB = pyomo.Var(model.Batteries, model.Blocks, bounds=boundProdB)
    # lines transfer limits
    model.line = pyomo.Var(model.Circuits, model.Blocks, bounds=boundLines)
    # spilled outflow of hydro plant
    model.spillH = pyomo.Var(model.Hydro, model.Blocks, domain=pyomo.NonNegativeReals)
    # energy non supplied
    model.deficit = pyomo.Var(model.Areas, model.Blocks, bounds=boundDeficit)
    # energy in nodes - balance
    model.balance = pyomo.Var(model.Areas, model.Blocks)
    # final volume
    model.vol = pyomo.Var(model.Hydro, bounds=boundVolH)
    # final battery level
    model.lvl = pyomo.Var(model.Batteries, bounds=boundlvlB)
    # future cost funtion value
    model.futureCost = pyomo.Var(domain=pyomo.NonNegativeReals)
    # spilled outflow of hydro plant
    model.spillW = pyomo.Var(model.Areas, model.Blocks, domain=pyomo.NonNegativeReals)
    # limit of storage at each block
    model.lvlBlk = pyomo.Var(model.Batteries, model.Blocks, bounds=boundlvlBlock)

    # conditional constraints
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
        
        
    # OBJ FUNCTION
    # total cost of thermal production
    if Param.emissions is True:
        # Consideration of CO2 emissions
        def obj_expr(model):
            return (sum((model.cost[t] * model.prodT[t, b]) for t in model.Thermal for b in model.Blocks) +
                    sum((model.hydroCost[h] * model.prodH[h, b]* model.factorH[h]) for h in model.Hydro for b in model.Blocks) +
                    sum((model.rationing[area] * model.deficit[area, b]) for area in model.AreasDmd for b in model.Blocks) +
                    model.futureCost +
                    # emissions
                    model.co2cost * ( sum(( model.hydroFE[h] * model.prodH[h, b]* model.factorH[h]) for h in model.Hydro for b in model.Blocks) + 
                    sum(( model.thermalFE[t] * model.prodT[t, b]) for t in model.Thermal for b in model.Blocks) +
                    sum(( model.smallFE[m] * model.prodS[m, b]) for m in model.Small for b in model.Blocks) )
                    )
        # Objective function
        model.OBJ = pyomo.Objective(rule=obj_expr)
    
    else:
        # Standard formulation
        def obj_expr(model):
            return (sum((model.cost[t] * model.prodT[t, b]) for t in model.Thermal for b in model.Blocks) +
                    sum((model.hydroCost[h] * model.prodH[h, b]* model.factorH[h]) for h in model.Hydro for b in model.Blocks) +
                    sum((model.rationing[area] * model.deficit[area, b]) for area in model.AreasDmd for b in model.Blocks) +
                    model.futureCost)
        # Objective function
        model.OBJ = pyomo.Objective(rule=obj_expr)
        
    # CONSTRAINTS
    # define constraint: demand must be served in each block and stage
    if Param.param_opf is True:
        def ctDemand(model, area, b):
            return (sum(model.prodT[t, b] for t in model.ThermalArea[area]) +
                    sum(model.prodS[m, b] for m in model.SmallArea[area]) +
                    sum(model.prodH[h, b]*model.factorH[h] for h in model.HydroArea[area]) +
                    sum(model.prodB[r, b] for r in model.Batteries if model.BatteriesArea[r] == area) +
                    sum(model.prodW[a, b] for a in model.AreasRnw if a == area ) + 
                    model.balance[area,b] + model.deficit[area, b] >= model.demand[area, b])
        # add constraint to model according to indices
        model.ctDemand = pyomo.Constraint(model.Areas, model.Blocks, rule=ctDemand)
        
        # energy balace in nodes
        def ctBalance(model, area, b):
            return (sum(model.line[l, b] for l in model.linesAreaOut[area]) - 
                    sum(model.line[l, b] for l in model.linesAreaIn[area])  ==
                    model.balance[area,b])
        model.ctBalace = pyomo.Constraint(model.Areas, model.Blocks, rule=ctBalance)
        
        # define opf constraints
        def ctOpf(model, ct, b):
            return( sum(model.balance[area,b] * model.flines[ct, area]
                    for area in model.Areas if (ct, area) in model.linebus) <= model.line[ct, b])
        # add constraint to model according to indices
        model.ctOpf = pyomo.Constraint(model.Circuits, model.Blocks, rule=ctOpf)
    
    else:
        def ctDemand(model, area, b):
            return (sum(model.prodT[t, b] for t in model.ThermalArea[area]) +
                    sum(model.prodS[m, b] for m in model.SmallArea[area]) +
                    sum(model.prodH[h, b]*model.factorH[h] for h in model.HydroArea[area]) +
                    sum(model.prodB[r, b] for r in model.Batteries if model.BatteriesArea[r] == area) +
                    sum(model.prodW[a, b] for a in model.AreasRnw if a == area ) + 
                    sum(model.line[l, b] for l in model.linesAreaOut[area]) -
                    sum(model.line[l, b] for l in model.linesAreaIn[area]) +
                    model.deficit[area, b] >= model.demand[area, b])
        # add constraint to model according to indices
        model.ctDemand = pyomo.Constraint(model.Areas, model.Blocks, rule=ctDemand)
    
    # define constraint: volume conservation
    def ctVol(model, h) :
        return (model.iniVol[h] + model.inflows[h] -
                sum(model.prodH[h, b] for b in model.Blocks) -
                sum(model.spillH[h, b] for b in model.Blocks) +
                sum(sum(model.prodH[hup, b] for b in model.Blocks) for hup in model.Hydro if (hup, h) in model.TurbiningArcs) +
                sum(sum(model.spillH[sup, b] for b in model.Blocks) for sup in model.Hydro if (sup, h) in model.SpillArcs) ==
                model.vol[h] )
    # add constraint to model according to indices
    model.ctVol = pyomo.Constraint(model.Hydro, rule=ctVol)

    # energy conservation by block
    def ctLvlBlk(model, r, b):
        return (model.iniLvlBlk[r, b] + model.chargeB[r, b]*model.factorB[r] -
                model.prodB[r, b]/model.factorB[r] == model.lvlBlk[r, b])
    # add constraint to model according to indices
    model.ctLvlBlk = pyomo.Constraint(model.Batteries, model.Blocks, rule=ctLvlBlk)

    # energy conservation by stage
    def ctLvl(model, r):
        return (model.iniLvl[r] +
                sum(model.chargeB[r, b]*model.factorB[r] for b in model.Blocks) -
                sum(model.prodB[r, b]/(model.factorB[r]) for b in model.Blocks) == model.lvl[r])
    # add constraint to model according to indices
    model.ctLvl = pyomo.Constraint(model.Batteries, rule=ctLvl)

    # define constraint: Wind production conservation
    def ctGenW(model, area, b) :
        return (sum( model.chargeB[r, b] for r in model.Batteries if model.BatteriesArea[r] == area) +
                model.spillW[area, b] + model.prodW[area, b] == model.meanWind[area, b])
    # add constraint to model according to indices
    model.ctGenW = pyomo.Constraint(model.AreasRnw, model.Blocks, rule=ctGenW)

    # define constraint: future cost funtion
    def ctFcf(model, c) :
        return (sum((model.coefcTerm[h, c] * model.vol[h]) for h in model.resHydro) +
                sum((model.coefcBatt[r, c] * model.lvl[r]) for r in model.Batteries) +
                model.constTerm[c]  <= model.futureCost)
    # add constraint to model according to indices
    model.ctFcf = pyomo.Constraint(model.Cuts, rule=ctFcf)

    # flowgates constraints
    if Param.flow_gates is True:
        # define gate constraints
        def ctGates(model, gate, b):
            return( -model.gateLimt[gate,b] <=
                    sum(sum(model.balance[area,b] * model.flines[l, area] for area in model.Areas if (l, area) in model.linebus) 
                            for (gt,l,area) in model.gateLines if gt == gate) <= 
                    model.gateLimt[gate,b])
        # add constraint to model according to indices
        model.ctGates = pyomo.Constraint(model.Gates, model.Blocks, rule=ctGates)
        
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
                    
            for z in lenblk:
                for y in range(numAreas):
                    model.meanWind[y+1,z+1] = dict_windenergy['windenergy_area'][y][s][k][z]
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
                model.minlvlB[plant] = dict_batt["b_storage"][i][s][1]
                model.maxlvlB[plant] = dict_batt["b_storage"][i][s][0]
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
                lvlHydro,linTransfer,spillHydro,genwind,spillwind,genSmall,emsscurve) = saveiter(k,
                s,lenblk,thermalPlants,model,model.prodT,genThermal,model.prodH,model.prodB,
                model.deficit,model.chargeB,model.lvl,model.vol,hydroPlants,batteries,
                genHydro,genBatteries,loadBatteries,lvlBatteries,lvlHydro,genDeficit,
                numAreas,linTransfer,model.line,circuits,spillHydro,model.spillH,genwind,
                model.prodW,model.spillW,spillwind,genSmall,smallPlants,model.prodS,rnwArea,
                Param,emissCurve)

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
        "emsscurve":emsscurve}

        pickle.dump(DataDictionary, open( "savedata/results_save.p", "wb" ) )

    return (sol_vol_iter, sol_lvl_batt, sol_cost_scn, sol_scn)

