
import pickle

def data(file):
    
    # Reading system information
    from scripts.readData import data_file
    print('Reading data...')
    data_file('datasystem/{}.xlsx'.format(file))
    # delete temporal files

def data_consistency(Param):
    
    from utils.paramvalidation import paramlimits
    
    # Load the dictionary back from the pickle file
    dict_data = pickle.load(open("savedata/data_save.p", "rb"))
    # No of maximum number of stages
    noStages = len(dict_data['horizon'])
    
    # validating input parameters
    paramlimits(Param, noStages)

def parameters(Param): #param_calculation,sensDem,stages,eps_area,eps_all):
    
    # Load the dictionary back from the pickle file
    dict_data = pickle.load(open("savedata/data_save.p", "rb"))
    
    # calculation options SI or NO
    if Param.param_calc is True:
        print('Parameters calculation ...')
    
        # Creating fixed input files '''
        from utils.input_data import inputdata
        inputdata(dict_data, Param.sensDem)
    
        from utils.input_hydro import inputhydro
        inputhydro(dict_data)
    
        from utils.input_wind import inputwindSet, inputInflowWind
        inputwindSet(dict_data, Param.stages, 1, 0)
        inputInflowWind(dict_data, Param.stages, Param.eps_area, Param.eps_all)
    
        from utils.input_others import inputbatteries, inputlines
        inputbatteries(dict_data, Param.stages)
        inputlines(dict_data, Param.stages)
    
def grid(param_opf, stages):
    
    # opf restrictions
    if param_opf is True:
        print('Parameters opf ...')
    
        from utils.opf_data import ybus
        ybus(stages)

def wmodel2(wind_model2, stages, seriesBack):
    
    # Load the dictionary back from the pickle file
    dict_data = pickle.load(open("savedata/data_save.p", "rb"))
    
    # Including wind power plants with model 2
    if wind_model2 is True:
        print('Model of wind power plants with losses ...')
    
        from utils.readWind import historical10m, format10m
        historical10m()
        format10m()
    
        from utils.input_wind import inputwindSet #, inputInflowWind, energyRealWind
        inputwindSet(dict_data, stages, 0, 1)
        # factores = energyRealWind(dict_data, seriesBack, stages)
        
def optimization(Param):
    
    #import timeit
    #import numpy
    
    #start = timeit.default_timer()
    
    from scripts import forward
    from scripts import backward
    from scripts import optimality
    
    # Load the dictionary back from the pickle file
    dict_data = pickle.load(open("savedata/data_save.p", "rb"))
    
    # dictionaries
    batteries = dict_data['batteries']
    hydroPlants = dict_data['hydroPlants']
    dict_batt = pickle.load(open("savedata/batt_save.p", "rb"))
    
    # Iteration inf _ improve the states under evaluation
    sol_vol = [[] for x in range(Param.stages+1)] # Hydro iteration
    sol_lvl = [[] for x in range(Param.stages+1)] # Batteries iteration
    sol_vol[0].append(dict_data['volData'][0])
    sol_lvl[0].append([dict_data['battData'][0][x]*dict_batt["b_storage"][x][0][0] for x in range(len(batteries))])
    
    iteration = 0 # Counter for number of iterations
    confidence = 0 # stop criteria
    
    # Save operational cost by iteration
    operative_cost = [[], []]
    
    # define: parameter classes
    # deterministic / stochastic analysis
    stochastic = True
    if Param.seriesBack == 1: stochastic = False # Deterministic

        # export options SI or NO
    if Param.results is True: from utils.saveresults import printresults
    else: pass
        
    #==============================================================================
    # loop iterations
    if Param.policy is True:
    
        while not iteration >= Param.max_iter and not confidence >= 2:
    
            # save the FCF - backward steps
            fcf_backward = [[] for x in range(Param.stages+1)]
            fcf_backward[Param.stages]=[[[0]*len(hydroPlants), [0]*len(batteries), 0]]
    
            # Backward_Risk6_par to parallel simulation
            backward.data(Param, fcf_backward, sol_vol, iteration, sol_lvl, stochastic)
            
            # Forward stage - Pyomo module
            (sv_iter, sl_batt, sol_costs, sol_scn) = forward.data(confidence, Param, iteration, True)
            
            # save new cuts
            for s in range(Param.stages):
                # save the last solutions
                last_sol = [x/Param.seriesForw for x in sv_iter[s]]
                last_batt = [x/Param.seriesForw for x in sl_batt[s]]
                if last_sol not in sol_vol[s+1] or last_batt not in sol_lvl[s+1]:
                    sol_vol[s+1].append([x/Param.seriesForw for x in sv_iter[s]])
                    sol_lvl[s+1].append([x/Param.seriesForw for x in sl_batt[s]])
    
            # confidence
            confd, op_cost, op_inf = optimality.data(sol_costs, Param.seriesForw)
            confidence += confd
            iteration += 1
    
            # Saver results
            operative_cost[0].append(op_cost), operative_cost[1].append(op_inf)
    
            #end = timeit.default_timer()
            #print(end - start)
    
            if iteration == Param.max_iter or confidence == 2:
                datafcf = {"fcf_backward":fcf_backward, "sol_vol":sol_vol, "sol_lvl":sol_lvl, 'sol_scn':sol_scn}
                pickle.dump(datafcf, open("savedata/fcfdata.p", "wb"))
    
                # generate report
                if Param.results is True:
                    print('Writing results ...')
                    # results files and reports
                    printresults(Param, sol_scn)
            
            # partial results
            # print(sum(sol_costs[2])/seriesForw)
            # print([max(sol_costs[2]),min(sol_costs[2]),numpy.std(sol_costs[2])])
            # print(sol_costs[2])
    
    elif Param.policy is False and Param.simulation is True:
    
        # stages to be simulate
        iteration = 0
        confidence = 1
    
        # Forward stage - Pyomo module
        (sol_vol, sol_lvl, sol_costs, sol_scn) = forward.data(confidence, Param, iteration, False)
    
        # Saver results
        confidence, op_cost, op_inf = optimality.data(sol_costs,Param.seriesForw)
        operative_cost[0].append(op_cost), operative_cost[1].append(op_inf)
    
        # generate report
        if Param.results is True:
            print('Writing results ...')
            # results files and reports
            printresults(Param, sol_scn)
        
        # print(operative_cost)
    
    elif Param.policy is False and Param.simulation is False:
    
        if Param.results is True:
    
            # recover results
            dict_fcf = pickle.load(open("savedata/fcfdata.p", "rb"))
            sol_scn = dict_fcf['sol_scn']
    
            print('Writing results ...')
            # results files and reports
            printresults(Param, sol_scn)
            
