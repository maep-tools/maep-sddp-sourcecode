''' MAEP Planning model 

Universidad de los Andes
Bogotá - Colombia

Licence MIT
'''

# packages
import timeit
from scripts import run_model

# print and debug
# import sys
# sys.stdout = open('output_console', 'w')

# simulation time
start = timeit.default_timer()

#==============================================================================

# Parameters simulation
file = 'test_model'       # input file name (DataSystem location)

class Parameters:
    
    max_iter = 3             # Maximun number of iterations
    bnd_stages = 3           # Boundary stages
    stages = 3 + bnd_stages  # planning horizon: (months + bundary months)
    seriesBack = 3           # scenarios for the backward phase
    seriesForw = 3           # scenarios the forward phase
    
    # Parameters analysis
    sensDem = 1     # Demand factor
    eps_area = 0.5  # Short-term - significance level area
    eps_all = 0.5   # Short-term - significance level for the whole system
    eps_risk = 0.1  # long-term risk
    commit = 0.0    # risk-measure comminment
    
    # read data options
    read_data = True       # read the input file
    param_calc = True       # parameters calculation
    param_opf = True        # OPF model
    
    # model components
    wind_model2 = False     # Second model of wind plants (inconcluse)
    flow_gates = False      # Security constraints (inefficient)   
    emss_curve = True       # emissions curve calculation 
    thermal_co2 = [1, 1]    # Emission factor type selection [tech:Ton/Mwh, Fuel:MBTU/MWh]  
    
    # operation model options
    emissions = True        # ObjectiveFunction - emissions costs
    policy = True           # algorithm: backward and forward 
    simulation = False      # algorithm: only forward (it needs cost-to-go function)
    parallel = False        # parallelization module (inconcluse)
    
    # PRINT ORDER: 1. dispatch curves, 2. marginal cost
    results = True            # Print main variables 
    curves = [True, True]    # selection of secondary results (experimental)

#==============================================================================
# run model
run_model.execution(Parameters, file)
              
#==============================================================================

# print execution time
end = timeit.default_timer()
print(end - start)
