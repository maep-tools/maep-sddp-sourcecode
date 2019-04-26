
def backseq(Param,i,dict_data,dict_format,model,opt,none1,none2,dict_renenergy):

#    import cProfile, pstats, io
#    #from pstats import SortKey
#    pr = cProfile.Profile()
#    pr.enable()
    
    import pickle
    #from objbrowser import browse
    #from pyomo.util.timing import report_timing
    
    hydroPlants = dict_data['hydroPlants']
    batteries = dict_data['batteries']
    volData = dict_data['volData']
    numAreas = dict_data['numAreas']
    numBlocks = dict_format['numBlocks']
    df_inflow = dict_format['inflow_hydro']
    
    # renewables data
    if Param.short_term is False:
        df_renenergy = dict_renenergy['average_vec']
    else:
        if Param.dist_f[0] is True:
            dict_pleps = pickle.load(open("savedata/pleps_save.p", "rb"))
            numPleps = dict_pleps['plepcount']
            residual = dict_pleps['p_points']
        elif Param.dist_f[1] is True:
            dict_pleps = pickle.load(open("savedata/pleps_save.p", "rb"))
            numPleps = dict_pleps['plepcount']
            residual = dict_pleps['p_points']
        elif Param.wind_aprox is True:
            df_renenergy = dict_renenergy['windenergy_area']
        
    # save data
    objective_list = []; total_obj = 0
    duals_batt = [[] for x in range(len(batteries))]
    duals = [[] for x in range(len(hydroPlants))]

    for k in range(Param.seriesBack):

        # Modifying input file: coefficient phi and constant delta; initial state; storage unit limits

        InflowsHydro = []
        InflowsHydro += [df_inflow[n][1][i-1][k] for n in range(len(hydroPlants))]

        for z in range(len(hydroPlants)):
            model.inflows[hydroPlants[z]] = InflowsHydro[z]
        
        if Param.short_term is False:
            
            # wind energy
            for z in range(numAreas):
                for y in range(numBlocks):
                    model.meanRen[z+1,y+1] = df_renenergy[z][i-1][k][y]
            
        else:
        
            if Param.dist_f[0] is True:
                # update rationing cost and demand values by stage
                for area1 in range(numAreas):
                    for y in range(numBlocks):
                        for plp in range(numPleps):
                            model.plep[area1+1, y+1, plp+1] = residual[i-1][k][area1][y][plp]
            elif Param.dist_f[1] is True:
                # update rationing cost and demand values by stage
                for area1 in range(numAreas):
                    for y in range(numBlocks):
                        for plp in range(numPleps):
                            model.plep[area1+1, y+1, plp+1] = residual[i-1][k][area1][y][plp]
            elif Param.wind_aprox is True:
                # wind energy
                for z in range(numAreas):
                    for y in range(numBlocks):
                        model.meanRen[z+1,y+1] = df_renenergy[z][i-1][k][y]
            
        # Reconstruct the instance and solve
        #model.ctVol.reconstruct(); model.ctGenW.reconstruct()

        opt.solve(model)#, symbolic_solver_labels=False)
        #model.display()
        #with open('pyomo_model.txt', 'w') as f:
        #    model.pprint(ostream=f)
        #browse(model)
        #report_timing()
        
        # duals solution related to volume and storage-batteries conservation constraint
        d_object = getattr(model, 'ctVol')
        for plant in range(len(hydroPlants)):
            if (volData[2][plant] > 0 and volData[3][plant] > 0):
                duals[plant].append(model.dual[d_object[hydroPlants[plant]]])
            else:
                duals[plant].append(0)
            #print(model.dual[d_object[hydroPlants[plant]]])
            #print(d_object[hydroPlants[plant]])
        #print(duals)
        d_object = getattr(model, 'ctLvl')
        for plant in range(len(batteries)):
            duals_batt[plant].append(model.dual[d_object[batteries[plant]]])

        # objective function value
        sol_objective = model.OBJ()
        #print(sol_objective)
        objective_list.append([sol_objective,k])
        total_obj += sol_objective

    #print(duals)
    
#    pr.disable()
#    s = io.StringIO()
#    #sortby = SortKey.CUMULATIVE
#    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')#sortby)
#    ps.print_stats()
#    #print(s.getvalue())
#    pr.print_stats(sort='time')
#    
#    with open('time_model.txt', 'w') as f:
#        f.write(s.getvalue())
        
    return objective_list,duals_batt,duals,total_obj

def backpar(scenarios,i,dict_data,dict_format,model,none,SolverFactory,
            SolverManagerFactory,dict_windenergy):

    import sys
    #from objbrowser import browse

    solver_manager = SolverManagerFactory('pyro')
    if solver_manager is None:
        print ("Failed to create solver manager.")
        sys.exit(1)

    hydroPlants = dict_data['hydroPlants']
    batteries = dict_data['batteries']
    volData = dict_data['volData']
    numareas = dict_data['numAreas']
    numBlocks = dict_format['numBlocks']
    df_inflow = dict_format['inflow_hydro']
    df_windenergy = dict_windenergy['windenergy_area']

    # save data
    objective_list = []; total_obj = 0
    duals_batt = [[] for x in range(len(batteries))]
    duals = [[] for x in range(len(hydroPlants))]

    # loop scenarios
    action_map = dict()
    # maps action handles to instances
    with solver_manager as manager:

        opt_solver = SolverFactory('gurobi')#, solver_io='python')
        opt_solver.options['threads'] = 4

        for k in range(scenarios):

            InflowsHydro = []
            InflowsHydro += [df_inflow[n][1][i-1][k] for n in range(len(hydroPlants))]

            for z in range(len(hydroPlants)):
                model.inflows[hydroPlants[z]] = InflowsHydro[z]
            for z in range(numareas):
                for y in range(numBlocks):
                    model.meanRen[z+1,y+1] = df_windenergy[z][i-1][k][y]

            # Reconstruct the instance and solve
            #instance.ctVol.reconstruct(); instance.ctGenW.reconstruct()
            #instance.dual = Suffix(direction=Suffix.IMPORT)

            action_map[manager.queue(model, opt=opt_solver, load_solutions=False)] = model
            #load_solutions=False

    for k in range(scenarios):

        a_m = manager.wait_any()
        instance_local=action_map[a_m]
        results = manager.get_results(a_m)
        #browse(results)

        # objective function value
        instance_local.solutions.load_from(results)
        sol_objective = instance_local.OBJ()
        #browse(instance_local)
        objective_list.append([sol_objective,k])
        total_obj += sol_objective

        # duals solution related to volume and storage-batteries conservation constraint
        d_object = getattr(model, 'ctVol')
        for plant in range(len(hydroPlants)):
            if (volData[2][plant] > 0 and volData[3][plant] > 0):
                duals[plant].append(instance_local.dual[d_object[hydroPlants[plant]]])
            else:
                duals[plant].append(0)
            #print(d_object[hydroPlants[plant]])
        #print(duals)
        d_object = getattr(model, 'ctLvl')
        for plant in range(len(batteries)):
            duals_batt[plant].append(instance_local.dual[d_object[batteries[plant]]])

#        for constr in range(len(hydroPlants)):
#            obj_dual = results.solution.constraint['c'+str(constr)]
#            index_p = hydroPlants.index(sorted(hydroPlants)[constr])
#            duals[index_p].append(obj_dual.get('Dual'))
#
#        for constr in range(len(batteries)):
#            obj_dual = results.solution.constraint['c'+str(constr+len(hydroPlants))]
#            index_p = batteries.index(sorted(batteries)[constr])
#            duals_batt[constr].append(obj_dual.get('Dual'))

    return objective_list,duals_batt,duals,total_obj