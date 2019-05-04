
def gurobi_solver(SolverFactory):
    
    # sometimes error magic number
    # find . -name '*.pyc' -delete
    
    #opt = SolverFactory('gurobi_persistent') 
    
    # line 268
    #stdin=('from gurobipy import *; '
    #       'print(gurobi.version()); exit()'),
                                              
    # Create a solver
    #opt = SolverFactory('gurobi')
    #opt = SolverFactory('gurobi_ampl')
    opt = SolverFactory('gurobi', solver_io='python')
    #opt = SolverFactory('gurobi', solver_io='direct')
    #opt.options['Threads'] = 4
    opt.options['symbolic_solver_labels'] = False
    opt.options['OutputFlag'] = 0
    opt.options['stream_solver'] = False
    opt.options['keepfiles'] = False
    opt.options['LogFile'] = ''
    opt.options['LogToConsole'] = 0
#    opt.options['MIPGap'] = 0.05

    return opt

def glpk_solver(SolverFactory):

    # Create a solver
    opt = SolverFactory('glpk')
    
    return opt

def cplex_solver(SolverFactory):

    # Create a solver
    opt = SolverFactory('cplex',solver_io='python')
    #opt = SolverFactory('cplex')
    #opt = SolverFactory('cplex',solver_io='nl')
    #opt = SolverFactory('cplexamp')
    #opt.options['stream_solver'] = False
    #opt.options['keepfiles'] = False
    
    return opt

def  ipopt_solver(SolverFactory):

    # Create a solver
    opt = SolverFactory("ipopt", solver_io='nl')
    #opt = SolverFactory("ipopt", solver_io='python')
    #opt = SolverFactory("ipopt")
    opt.options['nlp_scaling_method'] = 'user-scaling'
    #opt.options['stream_solver'] = False
    #opt.options['keepfiles'] = False
    
    return opt

def  cbc_solver(SolverFactory):

    # Create a solver
    opt = SolverFactory("cbc")#, solver_io='python')
    #opt = SolverFactory("cbc", solver_io='nl')
    #opt.options['nlp_scaling_method'] = 'user-scaling'
    opt.options['stream_solver'] = False
    opt.options['keepfiles'] = False
    
    return opt

def  xpress_solver(SolverFactory):

    # Create a solver
    opt = SolverFactory('xpress')
    #opt.options['logfile'] = 'CON:'
    #opt.options['gomcuts'] = 0
    
    return opt