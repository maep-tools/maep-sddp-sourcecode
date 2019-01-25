def fisrt_vec(weightvec2,probvec,eps_all):
    
    import pyomo.environ as pyomo
    from pyomo.opt import SolverFactory

    opt = SolverFactory('gurobi', solver_io='python')
    #opt = SolverFactory('gurobi')
    #opt = SolverFactory('cplex',solver_io='python')
    #opt = SolverFactory('cplex')
    #opt = SolverFactory('cplex',solver_io='nl')
    
    model = pyomo.ConcreteModel()

    stat = list(range(1, len(weightvec2[0])+1))
        
    # set of potential string lengths
    model.States = pyomo.Set(initialize= stat)
    model.Scenarios = pyomo.Set(initialize= list(range(1, len(weightvec2)+1)))
    
    # parameters
    model.prob = pyomo.Param(model.Scenarios, mutable=True)
    model.weight = pyomo.Param(model.Scenarios, model.States, mutable=True)
    
    # variables
    model.plep = pyomo.Var(model.States, within=pyomo.NonNegativeIntegers)
    model.bin = pyomo.Var(model.Scenarios, within=pyomo.Binary)
        
    # define the objective function
    def cost_rule(model):
        return sum(model.plep[s] for s in model.States)
    model.cost = pyomo.Objective(rule=cost_rule)
    
    def defvar(model, t, s):
        return (model.plep[t] - (model.weight[s,t]*(1-model.bin[s])) ) >= 0
    model.defvar = pyomo.Constraint(model.States, model.Scenarios, rule=defvar)
    
    def confidence(model):
        return sum(model.prob[i]*model.bin[i] for i in model.Scenarios) <=  eps_all
    model.confidence = pyomo.Constraint(rule=confidence)
    
    for i in range(len(weightvec2)): 
        model.prob[i+1] = round(probvec[i],5)
        for j in range(len(weightvec2[0])):
            model.weight[i+1,j+1] = weightvec2[i][j]    
    
    opt.solve(model)
    #with open('pyomo_model.txt', 'w') as f:
    #    model.pprint(ostream=f)
    # instance.display()
    
    first_plep = [] # Save results of initial plep
    for p_e in [model.plep]:
        varobject = getattr(model, str(p_e))
        first_plep.append( [varobject[i].value for i in stat] )
    
    return first_plep

def pelp_vec(weightvec2,probvec,first_plep,iteration,maxD,eps_all):
    
    import pyomo.environ as pyomo
    from pyomo.opt import SolverFactory

    opt = SolverFactory('gurobi', solver_io='python')
    model = pyomo.ConcreteModel()

    stat = list(range(1, len(weightvec2[0])+1))
        
    # set of potential string lengths
    model.States = pyomo.Set(initialize= stat)
    model.Scenarios = pyomo.Set(initialize= list(range(1, len(weightvec2)+1)))
    model.Iteration = pyomo.Set(initialize= list(range(1, iteration+1)))
    
    # parameters
    model.prob = pyomo.Param(model.Scenarios, mutable=True)
    model.maxd = pyomo.Param(model.States, mutable=True)
    model.weight = pyomo.Param(model.Scenarios, model.States, mutable=True)
    model.pevec = pyomo.Param(model.Iteration, model.States, mutable=True)
    
    # variables
    model.plep = pyomo.Var(model.States, within=pyomo.NonNegativeIntegers)
    model.bin = pyomo.Var(model.Scenarios, within=pyomo.Binary)
    model.binAux1 = pyomo.Var(model.Iteration, model.States, within=pyomo.Binary)
    model.binAux2 = pyomo.Var(model.Iteration, model.States, within=pyomo.Binary)  
        
    # define the objective function
    def cost_rule(model):
        return sum(model.plep[s] for s in model.States)
    model.cost = pyomo.Objective(rule=cost_rule)
    
    def defvar(model, t, s):
        return (model.plep[t] - (model.weight[s,t]*(1-model.bin[s])) ) >= 0
    model.defvar = pyomo.Constraint(model.States, model.Scenarios, rule=defvar)
    
    def confidence(model):
        return sum(model.prob[i]*model.bin[i] for i in model.Scenarios) <=  eps_all
    model.confidence = pyomo.Constraint(rule=confidence)
    
    def defbin1(model, r, s):
        return  model.plep[s] - model.pevec[r,s] + 1 <= model.maxd[s] * model.binAux1[r,s]
    model.defbin1 = pyomo.Constraint(model.Iteration, model.States, rule=defbin1)
    
    def defbin2(model, r, s):
        return  model.maxd[s]*(1-model.binAux1[r,s]) >= model.binAux2[r,s]
    model.defbin2 = pyomo.Constraint(model.Iteration, model.States, rule=defbin2)
    
    def defbin3(model, r):
        return sum( model.binAux2[r,s] for s in model.States) >= 1
    model.defbin3 = pyomo.Constraint(model.Iteration, rule=defbin3)
    
    # parameters
    for i in range(len(weightvec2)): 
        model.prob[i+1] = float("{0:.4f}".format(probvec[i]))
        for j in range(len(weightvec2[0])):
            model.weight[i+1,j+1] = weightvec2[i][j]
    
    for j in range(len(maxD)):
        model.maxd[j+1] = maxD[j]
    
    for i in range(iteration): 
        for z in range(len(first_plep[0])):
            model.pevec[i+1,z+1] = first_plep[i][z]
    
    # solving
    opt.solve(model)
    #with open('pyomo_model.txt', 'w') as f:
    #    model.pprint(ostream=f)
    # instance.display()
    
    # save results
    for p_e in [model.plep]:
        varobject = getattr(model, str(p_e))
        vec_res = [varobject[i].value for i in stat]
    
    return vec_res
    