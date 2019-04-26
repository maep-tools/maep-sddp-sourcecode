
import pickle

def data(Param, file):
    
    # Reading system information
    from scripts.readData import data_file
    print('Reading data...')
    data_file(Param, 'datasystem/{}.xlsx'.format(file))
    # delete temporal files

def data_consistency(Param):
    
    from utils.paramvalidation import paramlimits, valmodel
    
    # validating input parameters
    paramlimits(Param)
    valmodel(Param)

def parameters(Param): 
    
    # Load the dictionary back from the pickle file
    dict_data = pickle.load(open("savedata/data_save.p", "rb"))
    
    # calculation options SI or NO
    if Param.param_calc is True:
        print('Parameters calculation ...')
    
        # Creating fixed input files '''
        from utils.input_data import inputdata
        inputdata(dict_data, Param)
    
        from utils.input_hydro import inputhydro
        inputhydro(dict_data, Param)
        
        # wind speed data
        from utils.input_wind import inputwindSet
        inputwindSet(dict_data, Param)
        
        # solar radiation data
        from utils.input_solar import inputsolar
        inputsolar(dict_data, Param)
        
        # short-term analysis
        if Param.short_term is False:
            # Average analysis
            
            from utils.input_average import inputAvrWind
            from utils.input_average import inputAvrSolarL, inputAvrSolarD
            from utils.residualload import aggr_avr_energy
                
            inputAvrWind(dict_data, Param)
            inputAvrSolarL(dict_data, Param)
            inputAvrSolarD(dict_data, Param)
            aggr_avr_energy(dict_data, Param)
                
        else:
            # short-term models
            
            if Param.wind_model2 is True:
    
                from utils.input_wind import energyRealWind
                energyRealWind(dict_data,Param.seriesBack,Param.stages)
            
            # p-Efficient points calculation
            elif Param.dist_f[0] is True:
                
                from utils.input_wind_DF import inputDFWind
                from utils.input_solar_DF import inputDFSolarL, inputDFSolarD
                from utils.residualload import aggr_energy
                
                print('p-Efficient Points calculation ...')
                inputDFWind(dict_data, Param)
                inputDFSolarL(dict_data, Param)
                inputDFSolarD(dict_data, Param)
                aggr_energy(dict_data, Param)
            
            # MVE method
            elif Param.dist_f[1] is True:
                
                from utils.input_wind_DF import inputDFWind
                from utils.input_solar_DF import inputDFSolarL, inputDFSolarD
                from utils.residualload import aggr_energy
                
                print('p-Efficient Points calculation ...')
                inputDFWind(dict_data, Param)
                inputDFSolarL(dict_data, Param)
                inputDFSolarD(dict_data, Param)
                aggr_energy(dict_data, Param)
                
            elif Param.wind_aprox is True:
                
                from utils.input_wind import inputInflowWind
                inputInflowWind(dict_data, Param)
        
        from utils.input_others import inputbatteries, inputlines
        inputbatteries(dict_data, Param.stages)
        inputlines(Param, dict_data)
        
        #from utils.input_biomass import inputbiomass
        #inputbiomass(dict_data)
    
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
    
    from scripts import forward as forward
    #from scripts import forward2
    from scripts import backward as backward
    #from scripts import backward2
    from scripts import optimality
    
    # Load the dictionary back from the pickle file
    dict_data = pickle.load(open("savedata/data_save.p", "rb"))
    dict_batt = pickle.load(open("savedata/batt_save.p", "rb"))
    
    # dictionaries
    batteries = dict_data['batteries']
    hydroPlants = dict_data['hydroPlants']
    #biomassPlants = dict_data["biomassPlants"]
    
    # Iteration inf _ improve the states under evaluation
    sol_vol = [[] for x in range(Param.stages+1)] # Hydro iteration
    sol_lvl = [[] for x in range(Param.stages+1)] # Batteries iteration
    sol_stc = [[] for x in range(Param.stages+1)] # Batteries iteration
    
    sol_vol[0].append(dict_data['volData'][0])
    sol_lvl[0].append([dict_data['battData'][0][x]*dict_batt["b_storage"][x][0][0] for x in range(len(batteries))])
    sol_stc[0].append(dict_data['biomassData'][0])
    
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
            #fcf_backward2 = [[] for x in range(Param.stages+1)]
            #fcf_backward2[Param.stages]=[[[0]*len(hydroPlants), [0]*len(batteries), [0]*len(biomassPlants), 0]]
            
            # Backward_Risk6_par to parallel simulation
            backward.data(Param, fcf_backward, sol_vol, iteration, sol_lvl, stochastic)
            #backward2.data(Param, fcf_backward2, sol_vol, iteration, sol_lvl, stochastic)
            
            # Forward stage - Pyomo module
            (sv_iter, sl_batt, sol_costs, sol_scn) = forward.data(confidence, Param, iteration, True)
            #(sv_iter, sl_batt, sol_costs, sol_scn) = forward2.data(confidence, Param, iteration, True)
            
            # save new cuts
            for s in range(Param.stages):
                # save the last solutions
                #last_sol = [x/Param.seriesForw for x in sv_iter[s]]
                #last_batt = [x/Param.seriesForw for x in sl_batt[s]]
                #if last_sol not in sol_vol[s+1] or last_batt not in sol_lvl[s+1]:
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
                
                datafcf = {"operative_cost":operative_cost}
                pickle.dump(datafcf, open("savedata/operativecost.p", "wb"))
    
                # generate report
                if Param.results is True:
                    print('Writing results ...')
                    # results files and reports
                    printresults(Param)
            
            # partial results
            # print(sum(sol_costs[2])/Param.seriesForw)
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
        
        datafcf = {"operative_cost":operative_cost}
        pickle.dump(datafcf, open("savedata/operativecost.p", "wb"))
    
        # generate report
        if Param.results is True:
            print('Writing results ...')
            # results files and reports
            printresults(Param)
        
        # print(operative_cost)
    
    elif Param.policy is False and Param.simulation is False:
    
        if Param.results is True:
    
            # recover results
            dict_fcf = pickle.load(open("savedata/fcfdata.p", "rb"))
            sol_scn = dict_fcf['sol_scn']
    
            print('Writing results ...')
            # results files and reports
            printresults(Param)
            
