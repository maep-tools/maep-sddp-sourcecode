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
file = 'CS1cA'       # input file name (DataSystem location)

class Param:
    
    max_iter = 2              # Maximun number of iterations
    bnd_stages = 3           # Boundary stages
    stages = 30 + bnd_stages  # planning horizon: (months + bundary months)
    seriesBack = 3           # scenarios for the backward phase
    seriesForw = 3           # scenarios the forward phase
    
    # Parameters analysis
    sensDem = 1.5      # Demand factor
    eps_area = 0.5      # Short-term - significance level area
    eps_all = 0.05   # Short-term - significance level for the whole system
    eps_risk = 0.1  # long-term risk
    commit = 0.0    # risk-measure comminment
    
    # read data options
    read_data = True        # read the input file
    param_calc = True       # parameters calculation
    param_opf = False        # OPF model
    
    # renewables
    dist_free = False         # Free distribution model
    dist_samples = 10         # sample for p-efficient points calculation
    wind_model2 = False       # Second model of wind plants (inconcluse)

    # model components
    flow_gates = False      # Security constraints (inefficient)   
    emss_curve = False       # emissions curve calculation 
    thermal_co2 = [1, 1]    # Emission factor type selection [tech:Ton/Mwh, Fuel:MBTU/MWh]  
    
    # operation model options
    emissions = True        # ObjectiveFunction - emissions costs
    policy = False            # algorithm: backward and forward 
    simulation = False       # algorithm: only forward (it needs cost-to-go function)
    parallel = False         # parallelization module (inconcluse)
    
    # PRINT ORDER: 1. dispatch curves, 2. marginal cost
    results = True           # Print main variables 
    curves = [True, True]    # Selection of secondary results (experimental)

#==============================================================================
# run model
run_model.execution(Param, file)
              
#==============================================================================

# print execution time
end = timeit.default_timer()
print(end - start)

# validation: dist_free analysis do not consider renewable sources emission in the objective function
