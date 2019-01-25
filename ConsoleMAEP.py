''' MAEP Planning model 

e-mail: maep5600@gmail.com
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
file = '01_example_hydrothermal'       # input file name (DataSystem location)

class Param:
    
    max_iter = 3              # Maximun number of iterations
    bnd_stages = 6            # Boundary stages
    stages = 30 + bnd_stages  # planning horizon: (months + bundary months)
    seriesBack = 6            # scenarios for the backward phase
    seriesForw = 6            # scenarios the forward phase
    
    # Parameters analysis
    sensDem =  0.85      # Demand factor
    eps_area = 0.5       # Short-term - significance level area
    eps_all = 0.5        # Short-term - significance level for the whole system
    eps_risk = 0.1       # long-term risk
    commit = 0.15         # risk-measure comminment
    
    # read data options
    read_data = True         # read the input file
    param_calc = True        # parameters calculation
    
    # transmission network
    param_opf = False           # OPF model
    flow_gates = False          # Security constraints (inefficient calculation)
    
    # renewables
    dist_free = False            # Free distribution model (NO portfolio operation)
    dist_samples = 10            # sample for p-efficient points calculation
    wind_model2 = False          # Second model of wind plants (inconcluse)
    portfolio = [True,False]     # [storage-network, storage-wind]
                                 # [False,False] will be turn [True,False]
    # emissions
    emissions = True         # ObjectiveFunction - emissions costs
    emss_curve = True        # emissions curve calculation 
    thermal_co2 = [1, 1]     # Emission factor type selection [tech:Ton/Mwh, Fuel:MBTU/MWh]  
    
    # operation model options
    policy = False           # algorithm: backward and forward 
    simulation = False        # algorithm: only forward (it needs cost-to-go function)
    parallel = False          # parallelization module (inconcluse)

    # PRINT ORDER:  
    results = True          # Print main variables 

    # reports
    curves = [True,          # 1. dispatch curves
              False,         # 2. marginal cost
              [False,3],     # 3. Hydro generation scenarios, Number of plant
              False,         # 4. Wind/Renewables generation scenarios
              [False,26],    # 5. Charge and discharge of storage systems, stage to graph
              False,         # 6. Transfer of energy (requieres areas setting)
              True]          # 7. Emissions

#==============================================================================
# run model
run_model.execution(Param, file)
              
#==============================================================================

# print execution time
end = timeit.default_timer()
print(end - start)

# validation: dist_free analysis do not consider renewable sources emission in the objective function
