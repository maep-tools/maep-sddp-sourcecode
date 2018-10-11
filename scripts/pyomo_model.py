
def variables(model, pyomo):
    
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
    

def obj_function(Param, model, pyomo):
    
    # total cost of thermal production
    if Param.emissions is False:
        
        # Standard formulation
        def obj_expr(model):
            return (sum((model.cost[t] * model.prodT[t, b]) for t in model.Thermal for b in model.Blocks) +
                    sum((model.hydroCost[h] * model.prodH[h, b]* model.factorH[h]) for h in model.Hydro for b in model.Blocks) +
                    sum((model.rationing[area] * model.deficit[area, b]) for area in model.AreasDmd for b in model.Blocks) +
                    model.futureCost)
        # Objective function
        model.OBJ = pyomo.Objective(rule=obj_expr)
        
    else:
        
        if Param.dist_free is True:
                
            # Consideration of CO2 emissions
            def obj_expr(model):
                return (sum((model.cost[t] * model.prodT[t, b]) for t in model.Thermal for b in model.Blocks) +
                        sum((model.hydroCost[h] * model.prodH[h, b]* model.factorH[h]) for h in model.Hydro for b in model.Blocks) +
                        sum((model.rationing[area] * model.deficit[area, b]) for area in model.AreasDmd for b in model.Blocks) +
                        model.futureCost +
                        # emissions
                        model.co2cost * ( sum(( model.hydroFE[h] * model.prodH[h, b]* model.factorH[h]) for h in model.Hydro for b in model.Blocks) + 
                        sum(( model.thermalFE[t] * model.prodT[t, b]) for t in model.Thermal for b in model.Blocks) +
                        sum(( model.smallFE[m] * model.prodS[m, b]) for m in model.Small for b in model.Blocks) ) )
            # Objective function
            model.OBJ = pyomo.Objective(rule=obj_expr)
        
        else:
            
            # Consideration of CO2 emissions
            def obj_expr(model):
                return (sum((model.cost[t] * model.prodT[t, b]) for t in model.Thermal for b in model.Blocks) +
                        sum((model.hydroCost[h] * model.prodH[h, b]* model.factorH[h]) for h in model.Hydro for b in model.Blocks) +
                        sum((model.rationing[area] * model.deficit[area, b]) for area in model.AreasDmd for b in model.Blocks) +
                        model.futureCost +
                        # emissions
                        model.co2cost * ( sum(( model.hydroFE[h] * model.prodH[h, b]* model.factorH[h]) for h in model.Hydro for b in model.Blocks) + 
                        sum(( model.thermalFE[t] * model.prodT[t, b]) for t in model.Thermal for b in model.Blocks) +
                        sum(( model.smallFE[m] * model.prodS[m, b]) for m in model.Small for b in model.Blocks)
                        # sum(( model.windFE[a] * model.prodW[a, b]) for a in model.Areas for b in model.Blocks) 
                        # SOLAR AND WIND EMISSIONS TO BE IMPLEMENTED
                        ) )
            # Objective function
            model.OBJ = pyomo.Objective(rule=obj_expr)
            
def load_balance(Param, model, pyomo):
    
    if Param.param_opf is True:
        
        if Param.dist_free is True:
        
            def ctDemand(model, area, b):
                return (sum(model.prodT[t, b] for t in model.ThermalArea[area]) +
                        sum(model.prodS[m, b] for m in model.SmallArea[area]) +
                        sum(model.prodH[h, b]*model.factorH[h] for h in model.HydroArea[area]) +
                        sum(model.prodB[r, b] for r in model.Batteries if model.BatteriesArea[r] == area) +
                        model.balance[area,b] + model.deficit[area, b] >= model.RnwLoad[area, b] )
            # add constraint to model according to indices
            model.ctDemand = pyomo.Constraint(model.Areas, model.Blocks, rule=ctDemand)
            
            def ctRnwLoad(model, area, b):
                return( sum(model.factorPlep[area, b, p] * model.plep[area, b, p] for p in model.plepNum ) ==
                        model.RnwLoad[area, b] )
            # add constraint to model according to indices
            model.ctRnwLoad = pyomo.Constraint(model.Areas, model.Blocks, rule=ctRnwLoad)
            
            def ctPlep(model, area, b):
                return( sum(model.factorPlep[area, b, p] for p in model.plepNum ) == 1 )
            # add constraint to model according to indices
            model.ctPlep = pyomo.Constraint(model.Areas, model.Blocks, rule=ctPlep)
        
        else:
            
            def ctDemand(model, area, b):
                return (sum(model.prodT[t, b] for t in model.ThermalArea[area]) +
                        sum(model.prodS[m, b] for m in model.SmallArea[area]) +
                        sum(model.prodH[h, b]*model.factorH[h] for h in model.HydroArea[area]) +
                        sum(model.prodB[r, b] for r in model.Batteries if model.BatteriesArea[r] == area) +
                        sum(model.prodW[a, b] for a in model.AreasRnw if a == area ) + 
                        model.balance[area,b] + model.deficit[area, b] >= 
                        model.demand[area, b])
            # add constraint to model according to indices
            model.ctDemand = pyomo.Constraint(model.Areas, model.Blocks, rule=ctDemand)
    
        # energy balace in nodes
        def ctBalance(model, area, b):
            return (sum(model.line[l, b] for l in model.linesAreaOut[area]) - 
                    sum(model.line[l, b] for l in model.linesAreaIn[area]) ==
                    model.balance[area,b])
        # add constraint
        model.ctBalace = pyomo.Constraint(model.Areas, model.Blocks, rule=ctBalance)
        
        # define opf constraints
        def ctOpf(model, ct, b):
            return( -model.lineLimit[ct,b] <= sum(model.balance[area,b] *  
                   model.flines[ct, area] for area in model.Areas if (ct, area) in model.linebus) <= model.lineLimit[ct,b] )
        # add constraint to model according to indices
        model.ctOpf = pyomo.Constraint(model.Circuits, model.Blocks, rule=ctOpf)
            
    else:
        
        if Param.dist_free is True:
            
            def ctDemand(model, area, b):
                return (sum(model.prodT[t, b] for t in model.ThermalArea[area]) +
                        sum(model.prodS[m, b] for m in model.SmallArea[area]) +
                        sum(model.prodH[h, b]*model.factorH[h] for h in model.HydroArea[area]) +
                        sum(model.prodB[r, b] for r in model.Batteries if model.BatteriesArea[r] == area) +
                        sum(model.line[l, b] for l in model.linesAreaOut[area])-
                        sum(model.line[l, b] for l in model.linesAreaIn[area]) +
                        model.deficit[area, b] >= model.RnwLoad[area, b] )
            # add constraint to model according to indices
            model.ctDemand = pyomo.Constraint(model.Areas, model.Blocks, rule=ctDemand)
            
            def ctRnwLoad(model, area, b):
                return( sum(model.factorPlep[area, b, p] * model.plep[area, b, p] for p in model.plepNum ) ==
                        model.RnwLoad[area, b] )
            # add constraint to model according to indices
            model.ctRnwLoad = pyomo.Constraint(model.Areas, model.Blocks, rule=ctRnwLoad)
            
            def ctPlep(model, area, b):
                return( sum(model.factorPlep[area, b, p] for p in model.plepNum ) == 1 )
            # add constraint to model according to indices
            model.ctPlep = pyomo.Constraint(model.Areas, model.Blocks, rule=ctPlep)
    
        else:
            
            def ctDemand(model, area, b):
                return (sum(model.prodT[t, b] for t in model.ThermalArea[area]) +
                        sum(model.prodS[m, b] for m in model.SmallArea[area]) +
                        sum(model.prodH[h, b]*model.factorH[h] for h in model.HydroArea[area]) +
                        sum(model.prodB[r, b] for r in model.Batteries if model.BatteriesArea[r] == area) +
                        sum(model.prodW[a, b] for a in model.AreasRnw if a == area ) + 
                        sum(model.line[l, b] for l in model.linesAreaOut[area])-
                        sum(model.line[l, b] for l in model.linesAreaIn[area]) +
                        model.deficit[area, b] >= model.demand[area, b])
            # add constraint to model according to indices
            model.ctDemand = pyomo.Constraint(model.Areas, model.Blocks, rule=ctDemand)
            
def energy_conservationB(model, pyomo):
    
    # define constraint: volume conservation
    def ctVol(model, h):
        return (model.stateVol[h] + model.inflows[h] -
                sum(model.prodH[h, b] for b in model.Blocks) -
                sum(model.spillH[h, b] for b in model.Blocks) +
                sum(sum(model.prodH[hup, b] for b in model.Blocks) for hup in model.Hydro if (hup, h) in model.TurbiningArcs) +
                sum(sum(model.spillH[sup, b] for b in model.Blocks) for sup in model.Hydro if (sup, h) in model.SpillArcs) == 
                model.vol[h])
    # add constraint to model according to indices
    model.ctVol = pyomo.Constraint(model.Hydro, rule=ctVol)

    # energy conservation by block
    def ctLvlBlk(model, r, b):
        return (model.stateLvlBlk[r, b] + model.chargeB[r, b]*model.factorB[r] -
                model.prodB[r, b]/model.factorB[r] == model.lvlBlk[r, b])
    # add constraint to model according to indices
    model.ctLvlBlk = pyomo.Constraint(model.Batteries, model.Blocks, rule=ctLvlBlk)

    # energy conservation by stage
    def ctLvl(model, r):
        return (model.stateLvl[r] +
                sum(model.chargeB[r, b]*model.factorB[r] for b in model.Blocks) -
                sum(model.prodB[r, b]/(model.factorB[r]) for b in model.Blocks) == model.lvl[r])
    # add constraint to model according to indices
    model.ctLvl = pyomo.Constraint(model.Batteries, rule=ctLvl)
    
def energy_conservationF(model, pyomo):
    
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
    
def storage_function(Param, model, pyomo):
    
    if Param.dist_free is True:
        
        # define constraint: Wind production conservation
        def ctGenW(model, area, b):
            return (sum(model.chargeB[r, b] for r in model.Batteries if model.BatteriesArea[r] == area) +
                    model.spillW[area, b] + model.prodW[area, b] == 0)
        # add constraint to model according to indices
        model.ctGenW = pyomo.Constraint(model.AreasRnw, model.Blocks, rule=ctGenW)
    
    else:
        
        # define constraint: Wind production conservation
        def ctGenW(model, area, b):
            return (sum(model.chargeB[r, b] for r in model.Batteries if model.BatteriesArea[r] == area) +
                    model.spillW[area, b] + model.prodW[area, b] == model.meanWind[area, b])
        # add constraint to model according to indices
        model.ctGenW = pyomo.Constraint(model.AreasRnw, model.Blocks, rule=ctGenW)


def costtogo(Param, model, pyomo):
    
    # define constraint: future cost funtion
    def ctFcf(model, c):
        return (sum((model.coefcTerm[h, c] * model.vol[h]) for h in model.resHydro) +
                sum((model.coefcBatt[r, c] * model.lvl[r]) for r in model.Batteries) +
                model.constTerm[c] <= model.futureCost)
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
        
        