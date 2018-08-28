"""
Created on Tue Feb 13 09:39:31 2018

@author: da.pineros156
"""
#Esta función calcula la energía para un área, en una etapa, un escenario y un bloque
#Input: Información sobre las plantas, histórico de datos diezminutales, pronóstico mensual, a, et, esc, b
#Output: energía total para todas las áreas en MWh

import numpy as np

def prepareFactors(windFarmData,hist10mwind):

    ###############################################################################
    #Calculando factores para medias y desviaciones estándar en función de datos históricos
    #Asumimos que los caudales históricos se llaman así:
    #   Hist[pla][anho][mes][dia][hora] = [dm1, dm2, dm3, dm4, dm5, dm6]
    #Donde los dm son datos diezminutales
    
    #Matriz de factores vacía: factores[dato][planta][mes][hora], donde dato significa si es factor de media (0) o desv. estándar (1)                           
    factores = [[[[[] for i in range(24)] for j in range(12)] for k in range(len(windFarmData[0]))] for tipo in range(2)]   
         
    #Matriz de medias mensuales por año y por planta                                                  
    #Creando Matriz y llenándola
    #La Matriz está ordenada en términos de plantas... p=0 implica la primera planta
    mediash = [[[[] for i in range(12)] for j in range(len(hist10mwind[0])-1)] for k in range(len(windFarmData[0]))]  
    
    order = []
    for x in range(len(hist10mwind)):
        order.append(hist10mwind[x][0])
    
    for p in range(len(windFarmData[0])): # Para todas las plantas
        
        dataW = windFarmData[13][p]
        indexM = order.index(dataW)
        
        for m in range(12):   
                for a in range(len(hist10mwind[indexM])-1):
                    mediash[p][a][m]=np.mean(hist10mwind[indexM][a+1][1][m])
    
    #Llenar matriz de factores de medias y desviaciones intrahorarias
    for p in range(len(windFarmData[0])): #Para todas las plantas
        
        for m in range(12):
            for h in range(24):
                v=[]
                s=[]
                tam = len(hist10mwind[indexM])-1 #num anhos
                for a in range(tam):
                    tam2 = len(hist10mwind[indexM][a+1][1][m]) #num dias
                    for d in range(tam2):
                        data = hist10mwind[indexM][a+1][1][m][d][h]
                        test = [ isinstance(data[i],float) for i in range(len(data)) ] #Si todos son floats, guardar std
                        if np.sum(test) == 6:
                            s.append(np.std(data))
                        for i in range(len(data)):
                            if isinstance(data[i],float): #Si el dato es float, guardar la razón con su media mensual
                                v.append(data[i]/mediash[p][a][m])
                factores[0][p][m][h] = np.mean(v)
                factores[1][p][m][h] = np.mean(s)
    
    return factores

def prepareCurves(windFarmData,curvesData,speed_wind):
    
    import copy
    
    plantas = len(windFarmData[0])
            
    ###############################################################################
    # OJO, DEJAR DE SOBRESCRIBIR LA COSA
    #Interpolación de las curvas de potencia
    from scipy.interpolate import interp1d
    #Creando vector de velocidades
    curvesN = copy.deepcopy(curvesData)
    eta = len(speed_wind[0][1])
    entrance = [[[] for x in range(eta)] for p in range(plantas)]
    for pla in range(plantas):
        #pla=2
        vmin = windFarmData[2][pla]
        vmax = windFarmData[3][pla]
        res=windFarmData[4][pla]
        res_n=0.1
        v_iniciales = np.linspace(vmin,vmax,(vmax-vmin)/res+1)
        v_nuevas = np.linspace(vmin,vmax,(vmax-vmin)/res_n)
        #Obteniendo función y evaluando
        fpot = interp1d(v_iniciales, curvesData[pla][0], kind='cubic')
        fct = interp1d(v_iniciales, curvesData[pla][1], kind='cubic')
        CurPot = fpot(v_nuevas)
        CurCt = fct(v_nuevas)
        #Guardando nuevas curvas en curvesN
        #windFarmData[4][pla]=res_n
        curvesN[pla][0]=CurPot
        curvesN[pla][1]=CurCt
        curvesData[pla].append([])
        curvesData[pla][3] = v_nuevas
        for e in range(eta):
            if windFarmData[11][pla]-1 <= e: #Chequear indice 11 o 12
                entrance[pla][e] = 1
            else:
                entrance[pla][e] = 0
        
    return curvesData,curvesN,entrance


def e_areas(speed_wind,windFarmData,curvesData,curvesN,factores,entrance,et,es,b,numAreas): 
    
    import math
    
    plantas = len(windFarmData[0])

    ######################################################################### ######
    #Producción de energía del parque
    e_plantas = [[] for x in range(plantas)]
    loss=0.897 #Pérdidas además de la estela: 3% operativas, 7.5% envejecimiento
    res_n=0.1

    for p in range(plantas):
        #print("P ",p)
        mes=np.mod(et+1,12)
        if mes==0: 
            mes=11 
        else:
            mes=mes-1
        #Calculando las velocidades para todas las hileras de turbinas
        velh=speed_wind[p][1][et][es]*(windFarmData[6][p]/windFarmData[5][p])**windFarmData[7][p] #Ajustando por altura
        v=velh*factores[0][p][mes][b] #Multiplicando por la intensidad horaria
        if (v >= windFarmData[2][p] and v <= windFarmData[3][p] ):
            vmin = windFarmData[2][p]
            #res=windFarmData[4][p]
            v_round = np.round((v-vmin)/res_n)*res_n+vmin                  
            speeds=[]        
            speeds.append(v_round)
            num_hileras=len(curvesData[p][2])          
            for i in range(num_hileras-1):
                idx_v = int((speeds[i] - vmin)/res_n)+1 #REVISAR VELOCIDAD MÁXIMA
                if idx_v > 179:
                    idx_v = 179
                if idx_v < 0:
                    idx_v = 0
                f1 = 1-(1-curvesN[p][1][idx_v])**0.5
                k=0.075 #Para la Guajira
                f2 = 1- f1*(windFarmData[10][p]/(windFarmData[10][p]+2*k*windFarmData[9][p]))**2 #Chequear indices
                ve=speeds[i]*f2
                nv = np.round((ve-vmin)/res_n)*res_n+vmin 
                speeds.append(nv)
            
            #Calculando la producción de cada turbina
            dias = dias=[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            d=dias[mes] #Ignorando el día adicional en los bisiestos
            e=[]
            for i in range(num_hileras):     
                k_wei = (factores[1][p][mes][b]/speeds[i])**-1.086
                c_wei = speeds[i]/math.gamma(1+1/k_wei)
                wei=[]
                for v in range(len(curvesData[p][3])):
                    wei.append( (k_wei/c_wei)*np.exp(-(curvesData[p][3][v]/c_wei)**k_wei)*(curvesData[p][3][v]/c_wei)**(k_wei-1) )
                argint = np.dot(wei,curvesN[p][0])
                e.append(argint*res_n*loss*d/1000) #producción de 1 turbina en cada hilera EN MWH
            e_plantas[p] = np.dot(e,curvesData[p][2]) * entrance[p][et] #multiplicando por el # de turbinas por hilera y chequeando entrada
        else:
            e_plantas[p] = 0
    
    #Calculando totales por Áreas. Revisar NOMBRE O NÚMERO DE ÁREA
    e_areas = [0 for x in range(numAreas)]   
    for p in range(plantas):
        area = int(windFarmData[12][p])-1
        e_areas[area] = e_areas[area] + e_plantas[p]
    
    return e_areas