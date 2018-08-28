
def objdet(none1,none2,scenarios,none3,none4,hydroPlants,batteries,
           duals,duals_batt,total_obj):

    # save data
    delta_cut = 0; phi_risk = []; phi_batt_risk = []

    # calculate delta
    delta_cut = (total_obj/scenarios)

    # calculate coefficient Phi in risk measure
    for plant in range(len(hydroPlants)):
        duals_p = duals[plant]
        avg_dual = sum(duals_p)/scenarios
        phi_risk.append(-avg_dual)

    # calculate coefficient Phi in risk measure
    for plant in range(len(batteries)):
        duals_b = duals_batt[plant]
        avg_dual = sum(duals_b)/scenarios
        phi_batt_risk.append(-avg_dual)

    return delta_cut, phi_risk, phi_batt_risk

def objst(objective_list,int_bound,scenarios,commit,risk,hydroPlants,batteries,
          duals,duals_batt,total_obj):

    # save data
    delta_cut = 0; phi_risk = []; phi_batt_risk = []
    delta_cut =total_obj/scenarios
    
    # calculate coefficient Phi in risk measure
    for plant in range(len(hydroPlants)):
        duals_p = duals[plant]
        avg_dual = sum(duals_p)/scenarios
        phi_risk.append(-avg_dual)

    # calculate coefficient Phi in risk measure
    for plant in range(len(batteries)):
        duals_b = duals_batt[plant]
        avg_dual = sum(duals_b)/scenarios
        phi_batt_risk.append(-avg_dual)

    return delta_cut,phi_risk,phi_batt_risk

# CVaR
def objstrisk(objective_list,int_bound,scenarios,commit,risk,hydroPlants,batteries,
          duals,duals_batt,total_obj):

    # save data
    delta_cut = 0; phi_risk = []; phi_batt_risk = []

    # calculate delta
    objective_list.sort()
    objective_val = [z[0] for z in objective_list]; objective_diff = []; diff = []
    objective_diff[:] = [z - objective_val[int_bound-1] for z in objective_val]
    diff = [z if z>0 else 0 for z in objective_diff]
    diff = sum([x**2 for x in diff])/(scenarios-1)
    delta_cut =((1-commit)*(total_obj/scenarios)) + (commit*(objective_val[int_bound-1] + ((diff**0.5)/risk)))

    # calculate coefficient Phi in risk measure
    for plant in range(len(hydroPlants)):
        duals_p = duals[plant]
        avg_dual = sum(duals_p)/scenarios
        risk_dual = sum([duals_p[z] - duals_p[objective_list[int_bound-1][1]] if objective_diff[z]>0 else 0 for z in range(scenarios)])
        phi_risk.append(-((1-commit)*avg_dual)-(commit*(duals_p[objective_list[int_bound-1][1]]-(risk_dual/(scenarios*risk)))))

    # calculate coefficient Phi in risk measure
    for plant in range(len(batteries)):
        duals_b = duals_batt[plant]
        avg_dual = sum(duals_b)/scenarios
        risk_dual = sum([duals_b[z] - duals_b[objective_list[int_bound-1][1]] if objective_diff[z]>0 else 0 for z in range(scenarios)])
        phi_batt_risk.append(-((1-commit)*avg_dual)-(commit*(duals_b[objective_list[int_bound-1][1]]-(risk_dual/(scenarios*risk)))))

    return delta_cut,phi_risk,phi_batt_risk