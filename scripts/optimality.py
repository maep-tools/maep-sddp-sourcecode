def data(sol_costs,seriesForw):
    
    # bounds to verify the optimality
    b_inf = sum(sol_costs[1])/seriesForw
    
    # calculating the upper bound
    b_scenario = sum(sol_costs[0])/seriesForw
    
    # standar deviation of the stimator
    if seriesForw > 1:
        dev = (sum([(x-b_scenario)**2 for x in sol_costs[0]])**0.5)/(seriesForw-1)
    
    if seriesForw > 1:
        if b_inf > b_scenario-(1.96*dev) and b_inf < b_scenario+(1.96*dev):
            confidence = 1
        else:
            confidence = 0
    else:
        porcentaje = (b_scenario/b_inf)-1
        if porcentaje < 0.0005:
            confidence = 1
        else:
            confidence = 0
        
    return confidence, b_scenario, b_inf