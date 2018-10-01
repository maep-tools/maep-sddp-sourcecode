
def saveiter(k,s,lenblk,thermalPlants,instance,modelprodT,genThermal,modelprodH,
         modelprodB,modeldeficit,modelchargeB,modellvl,modelvol,hydroPlants,
         batteries,genHydro,genBatteries,loadBatteries,lvlBatteries,lvlHydro,
         genDeficit,numAreas,linTransfer,modelline,linesData,spillHydro,modelspillH,
         genwind,modelprodW,modelspillW,spillwind,genSmall,smallPlants,modelprodS,
         rnwArea,Param,emissCurve):
    
    import pickle
    dict_data = pickle.load(open("savedata/data_save_iter.p", "rb"))
    volData = dict_data['volData']
    thermalData = dict_data['thermalData']
    smallData = dict_data['smallData']
    
    # extracting results
    for gen_T in [modelprodT]: Tobject = getattr(instance, str(gen_T))
    for gen_S in [modelprodS]: Sobject = getattr(instance, str(gen_S))
    for gen_H in [modelprodH]: Hobject = getattr(instance, str(gen_H))
    for gen_W in [modelprodW]: Wobject = getattr(instance, str(gen_W))
    for spl_W in [modelspillW]: sWobject = getattr(instance, str(spl_W))
    for gen_B in [modelprodB]: Bobject = getattr(instance, str(gen_B))
    for gen_D in [modeldeficit]: Dobject = getattr(instance, str(gen_D))
    for load_B in [modelchargeB]: cBobject = getattr(instance, str(load_B))
    for lvl_B in [modellvl]: lBobject = getattr(instance, str(lvl_B))
    for lvl_H in [modelvol]: lHobject = getattr(instance, str(lvl_H))
    for spl_H in [modelspillH]: sHobject = getattr(instance, str(spl_H))
    for trf_L in [modelline]: linobject = getattr(instance, str(trf_L))

    for i, plant in enumerate(thermalPlants):
        for j in lenblk:
            genThermal[k][s][i][j] = Tobject[plant, j+1].value

    for i, plant in enumerate(smallPlants):
        for j in lenblk:
            genSmall[k][s][i][j] = Sobject[plant, j+1].value

    for i, plant in enumerate(hydroPlants):
        lvlHydro[k][s][i] = lHobject[plant].value
        for j in lenblk:
            genHydro[k][s][i][j] = Hobject[plant, j+1].value
            spillHydro[k][s][i][j] = sHobject[plant, j+1].value

    for i in range(numAreas):
        for j in lenblk:
            genDeficit[i][k][s][j] = Dobject[i+1,j+1].value
            spillwind[k][s][i][j] = sWobject[i+1, j+1].value
            if i+1 in rnwArea:
                genwind[k][s][i][j] = Wobject[i+1, j+1].value
            else:
                genwind[k][s][i][j] = 0

    for i, plant in enumerate(batteries):
        lvlBatteries[k][s][i] = lBobject[plant].value
        for j in lenblk:
            genBatteries[k][s][i][j] = Bobject[plant, j+1].value
            loadBatteries[k][s][i][j] = cBobject[plant,j+1].value

    if numAreas is not 1:
        for i in range(len(linesData)):
            org = linesData[i][0]; dest = linesData[i][1]
            for j in lenblk:
                linTransfer[k][s][org-1][dest-1].append(linobject[i+1, j+1].value)

    if Param.emss_curve is True:
        # save emissions curve
        for j in lenblk:
            aux1 = 0; aux2 = 0; aux3 = 0
            for i, plant in enumerate(thermalPlants):
                aux1 += genThermal[k][s][i][j] * ((Param.thermal_co2[0]*thermalData[13][i])+
                     (Param.thermal_co2[1]*thermalData[12][i]*thermalData[11][i]))
            for i, plant in enumerate(smallPlants):
                aux2 += genSmall[k][s][i][j] * smallData[8][i]
            for i, plant in enumerate(hydroPlants):
                aux3 += genHydro[k][s][i][j] * volData[15][i]
                
            emissCurve[k][s][j] = aux1 + aux2 + aux3
            
        return (genThermal,genHydro,genBatteries,genDeficit,loadBatteries,lvlBatteries,
                lvlHydro,linTransfer,spillHydro,genwind,spillwind,genSmall,emissCurve)
            
    else:
            
        return (genThermal,genHydro,genBatteries,genDeficit,loadBatteries,lvlBatteries,
                lvlHydro,linTransfer,spillHydro,genwind,spillwind,genSmall,emissCurve)

def printresults(Param,sol_scn):

    from reports_utils.dispatch import gendispatch
    from reports_utils.curves_report import marginalcost
    from utils.file_results import xlsfile

    # write results
    xlsfile(Param)

    # dispacht
    if Param.curves[0] is True: gendispatch(Param)

    # marginal costs
    if Param.curves[1] is True: marginalcost(Param)
