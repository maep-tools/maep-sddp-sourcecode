def chargedis(Param):
    
    import pickle
    dict_charts = pickle.load( open( "savedata/html_save.p", "rb" ) )
    dict_data = pickle.load( open( "savedata/data_save.p", "rb" ) )
    
    import plotly
    import plotly.graph_objs as go
    
    scenarios = Param.seriesForw
    genBFinal = dict_charts['genBBlockFinal']
    genBdisFinal = dict_charts['genBdisBlockFinal']
    
    scenarios = Param.seriesForw
    stage = Param.curves[4][1]-1
    
    x = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9',
     'B10', 'B11', 'B12', 'B13', 'B14', 'B15', 'B16', 'B17', 'B18',
     'B19', 'B20', 'B21', 'B22', 'B23', 'B24']
    
    ###########################################################################
    
    # all areas dispatch
    dict_fig ={}
    
    y2 = [(x-y)/scenarios for (x,y) in zip(genBFinal[stage],genBdisFinal[stage])]
    
    trace2 = go.Bar(
        x=x,
        y=y2,
        #name='Discharge',
        marker=dict(
            color='rgb(26, 118, 255)'
        )
    )
    
    data = [trace2]
    
    # Edit the layout
    layout = dict(
            autosize=False,
            width=1100,
            height=500,
            title = 'Charge and discharge of the storage systems',
            xaxis = dict(title = 'Stage '+str(stage)),
            yaxis = dict(title = 'Energy [MWh]'),
                  )
    
    #fig = dict(data=data, layout=layout)
    #py.iplot(fig, filename='styled-line')
    fig = go.Figure(data=data, layout=layout)
    dict_fig["aggr"] = plotly.offline.plot(fig, output_type = 'div')
    
    
    from jinja2 import Environment, FileSystemLoader
    
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("templates/storage_report.html")
    
    template_vars = {"title" : "Report",
                     "data1": "Charge and discharge",
                     "div_placeholder1A": dict_fig["aggr"]
                     #"div_placeholder1B": dict_fig["string2"],
                     #"div_placeholder1C": dict_fig["string3"],
                     #"div_placeholder1D": dict_fig["string4"],
                     #"div_placeholder1E": dict_fig["string5"],
                     #"data2": "All areas",
                     #"div_placeholder2": graf3,
                     #"data3": ,
                     #"div_placeholder3": ,
                     #"data4": ,
                     #"div_placeholder4": 
                     }
    
    html_out = template.render(template_vars)
    
    Html_file= open("results/report_variables/storage_report.html","w")
    Html_file.write(html_out)
    Html_file.close()
    
    
#    import os
#    import csv, pickle
#    import openpyxl
#    from utils.readxlxs import xlxstocsvsaved
#    from statistics import mean
#    
#    dict_data = pickle.load( open( "savedata/data_save.p", "rb" ) )
#    dict_batt = pickle.load( open( "savedata/batt_save.p", "rb" ) )
#    
#    horizon = dict_data["horizon"]
#    battData = [40,60] # dict_data["battData"][3]
#    # thermalData = dict_data["thermalData"]
#    # battNum = dict_batt["b_area"]
#     
#    
#    scenarios = 20
#    stages = 60
#    
#    # Historical data wind
#    alldata = []; alldata2 = []; title = []
#    dict_fig ={}
#    
#    path= 'saved_simulations/simulations/'
#    for root,dirs,files in os.walk(path):
#        xlsfiles=[ _ for _ in files if _.endswith('.xlsx') ]
#        for xlsfile in xlsfiles:
#            
#            # import file
#            importedfile = openpyxl.load_workbook(filename = os.path.join(root,xlsfile), read_only = True, keep_vba = False)
#            
#            tabnames = importedfile.get_sheet_names()
#            xlxstocsvsaved(tabnames,'LoadBatt',importedfile)
#            
#            with open('saved_simulations/csvreports/'+'LoadBatt'+'.csv') as csvfile:
#                readCSV = csv.reader(csvfile, delimiter=',')
#                singleData = [[[] for y in range(scenarios)] for x in range(len(battData))]
#                for row in readCSV:
#                    for bm in range(len(battData)):
#                        for col in range(scenarios):
#                            val = row[(col+2)+(bm+1)*scenarios-scenarios]
#                            try: 
#                                val = float(val)/battData[bm]
#                            except ValueError:
#                                pass
#                            singleData[bm][col].append(val)
#                
#            alldata.append(singleData)
#            title.append(xlsfile)
#    
#    vecdata = []
#    for i in range(len(alldata)):
#        vec = []
#        for x in range(len(battData)):
#            val = [0]*stages
#            maxval = [0]*stages; minval = [9999]*stages 
#            for j in range(scenarios):
#                vec2 = []
#                for z in range(stages):
#                    y = sum(alldata[i][x][j][4+(z+1)*24-24:4+(z+1)*24])
#                    vec2.append(y)
#
#                val = [sum(xc) for xc in zip(val, vec2)]
#                maxval = [max(xc) for xc in zip(maxval, vec2)]
#                minval = [min(xc) for xc in zip(minval, vec2)]
#            
#            val = [xc/scenarios for xc in val]
#            vec.append([val,maxval,minval])
#        vecdata.append(vec)
#            
#    #import datetime
#    #axisfixlow = horizon[23] + datetime.timedelta(hours = -360)
#    #axisfixhig = horizon[stages-1] + datetime.timedelta(hours = 360)
#    #x=horizon#list(range(1,stages+1))
#    
#    ############################################################################
#    
#    import plotly 
#    import plotly.graph_objs as go
#    import numpy as np
#
#    aux1 = [np.mean(vecdata[0][0][0][24:]), np.mean(vecdata[0][1][0][36:])]
#    aux2 = ['Storage 1','Storage 2']
#    aux11 = [0, 0]
#    
#    aux3 = [np.mean(vecdata[3][0][0][24:]), np.mean(vecdata[3][1][0][36:])]
#    aux33 = [np.mean(vecdata[1][0][0][24:]), np.mean(vecdata[1][1][0][36:])]
#    aux44 = [np.mean(vecdata[2][0][0][24:]), np.mean(vecdata[2][1][0][36:])]
#    #aux4 = ['Storage 1']*36+['Storage 2']*24
#    
#    # Create traces
#    trace0 = go.Bar(
#    y=aux1,
#    x=aux2,
#    name = 'Wind-neutral',
#    #width = [0.1, 0.1],
#    #jitter=0.32,
#    #fillcolor= 'rgb(255, 255, 255)',
#    #whiskerwidth=0.3,
#    #showlegend = False,
#    opacity=0.6,
#    marker=dict(color = 'rgb(0,71,133)',
#                line=dict(
#                color='rgb(0,71,133)',
#                width=1.5)
#            ),
#    #line=dict(width=1.5)
#    )
#    trace11 = go.Bar(
#    y=aux11,
#    x=aux2,
#    #width = [0.05, 0.05],
#    #name = title[0],
#    #boxpoints='all',
#    #jitter=0.32,
#    #fillcolor= 'rgb(255, 255, 255)',
#    #whiskerwidth=0.3,
#    showlegend = False,
#    #fillcolor=cls,
#    #marker=dict(
#    #        size=3,
#    #    ),
#    #line=dict(width=1.5)
#    )
#    trace2 = go.Bar(
#    y=aux3,
#    x=aux2,
#    #boxpoints = 'all',
#    name = 'Wind-risk',
#    opacity=0.6,
#    marker=dict(color = 'rgb(198,9,59)',
#                line=dict(
#                color='rgb(198,9,59)',
#                width=1.5)
#            ),
#    )
#        # Create traces
#    trace3 = go.Bar(
#    y=aux33,
#    x=aux2,
#    name = 'Risk-averse + Wind-risk',
#    opacity=0.6,
#    marker=dict(color = 'rgb(102,0,51)',
#                line=dict(
#                color='rgb(102,0,51)',
#                width=1.5)
#            ),
#    )
#    trace4 = go.Bar(
#    y=aux44,
#    x=aux2,
#    #boxpoints = 'all',
#    name = 'Risk-averse + Wind-neutral',
#    opacity=0.6,
#    marker=dict(color = 'rgb(0,107,51)',
#                line=dict(
#                color='rgb(0,107,51)',
#                width=1.5)
#            ),
#    )
#
#    data = [trace11, trace0, trace2, trace11, trace4, trace3, trace11]
#    
#    layout = go.Layout(
#    autosize=False,
#    width=720,
#    height=400,
#    barmode='group',
#    #title='Double Y Axis Example',
#    yaxis=dict(range=[0,82],
#               title=' Discharge-charge cycles',
#               titlefont=dict(
#                       family='Arial, sans-serif',
#                       size=18,
#                       color='black'),
#               #tickformat = ".0f"
#               #exponentformat = "e",
#               #showexponent = "none",
#               ticks = "inside",
#               tickfont=dict(
#                    #family='Old Standard TT, serif',
#                    size=14,
#                    color='black'
#                        )
#               ),
#    legend=dict(font=dict(
#                        #family='sans-serif',
#                        size=14,
#                        color='black'
#                        ),
#               orientation="h"),
#    xaxis = dict(#title = '1- ',
#                 #    titlefont=dict(
#                 #            #family='Arial, sans-serif',
#                 #            size=19,
#                 #            color='black'),
#                     tickfont=dict(
#                    #family='Old Standard TT, serif',
#                    size=14,
#                    color='black'
#                        )),
#    )
#               
#    fig = go.Figure(data=data, layout=layout)
#    dict_fig["aggr"] = plotly.offline.plot(fig, output_type = 'div', show_link=False)
#    
#    ###########################################################################
#        
#    from jinja2 import Environment, FileSystemLoader
#    
#    env = Environment(loader=FileSystemLoader('.'))
#    template = env.get_template("saved_simulations/templates_saved/storagecycles_report.html")
#    
#    template_vars = {"title" : "Report",
#                     "data1": "Each area dispatch",
#                     "div_placeholder1A": dict_fig["aggr"]
#                     #"div_placeholder1B": dict_fig["string2"],
#                     #"div_placeholder1C": dict_fig["string3"],
#                     #"div_placeholder1D": dict_fig["string4"],
#                     #"div_placeholder1E": dict_fig["string5"],
#                     #"data2": "All areas",
#                     #"div_placeholder2": graf3,
#                     #"data3": ,
#                     #"div_placeholder3": ,
#                     #"data4": ,
#                     #"div_placeholder4": 
#                     }
#    
#    html_out = template.render(template_vars)
#    
#    Html_file= open("saved_simulations/reports/storagecycles_report.html","w")
#    Html_file.write(html_out)
#    Html_file.close()
#
#def ciclesblock():
#    
#        #def aggregated():
#        
#    stages = 60
#    scenarios = 10
#    
#    import os
#    import csv, pickle
#    import openpyxl
#    from utils.readxlxs import xlxstocsvres
#    
#    # Historical data wind
#    alldata = []; alldata2 = []
#    dict_fig ={}
#    
#    dict_batt = pickle.load( open( "savedata/batt_save.p", "rb" ) )
#    
#    
#    path= 'resultsgeneral/'
#    for root,dirs,files in os.walk(path):
#        xlsfiles=[ _ for _ in files if _.endswith('.xlsx') ]
#        for xlsfile in xlsfiles:
#            
#            # import file
#            importedfile = openpyxl.load_workbook(filename = os.path.join(root,xlsfile), read_only = True, keep_vba = False)
#            
#            tabnames = importedfile.get_sheet_names()
#            xlxstocsvres(tabnames,'BatteriesGen',importedfile)
#            
#            with open('resultsgeneral/'+'BatteriesGen'+'.csv') as csvfile:
#                readCSV = csv.reader(csvfile, delimiter=',')
#                singleData = [[] for x in range(10)]  
#                for row in readCSV:
#                    for col in range(10):
#                        val = row[col+2]
#                        try: 
#                            val = float(val)
#                        except ValueError:
#                            pass
#                        singleData[col].append(val)
#            
#            alldata.append(singleData)
#    
#    vecdata = []
#    for i in range(len(alldata)):
#        vec = []
#        for z in range(60):
#            y = 0
#            for j in range(scenarios):
#                y += sum(alldata[i][j][4+(z+1)*24-24:2+(z+1)*24])
#            val = y/scenarios
#            
#            vec.append(val)
#        vecdata.append(vec)
#            
#    # dowload
#    for root,dirs,files in os.walk(path):
#        xlsfiles=[ _ for _ in files if _.endswith('.xlsx') ]
#        for xlsfile in xlsfiles:
#            
#            # import file
#            importedfile = openpyxl.load_workbook(filename = os.path.join(root,xlsfile), read_only = True, keep_vba = False)
#            
#            tabnames = importedfile.get_sheet_names()
#            xlxstocsvres(tabnames,'LoadBatt',importedfile)
#            
#            with open('resultsgeneral/'+'LoadBatt'+'.csv') as csvfile:
#                readCSV = csv.reader(csvfile, delimiter=',')
#                singleData = [[] for x in range(10)]  
#                for row in readCSV:
#                    for col in range(10):
#                        val = row[col+2]
#                        try: 
#                            val = float(val)
#                        except ValueError:
#                            pass
#                        singleData[col].append(val)
#            
#            alldata2.append(singleData)
#    
#    vecdata2 = []
#    for i in range(len(alldata2)):
#        vec = []
#        for z in range(60):
#            y = 0
#            for j in range(scenarios):
#                y += sum(alldata2[i][j][4+(z+1)*24-24:2+(z+1)*24])
#            val = y/scenarios
#            
#            vec.append(val)
#        vecdata2.append(vec)      
#            
#    
#    dict_data = pickle.load( open( "savedata/data_save.p", "rb" ) )
#    
#    #import plotly
#    #import plotly.graph_objs as go
#    
#    #    genHFinal = dict_charts['genHFinal']
#    #    genTFinal = dict_charts['genTFinal']
#    #    genWFinal = dict_charts['genWFinal']
#    #    genDFinal = dict_charts['genDFinal']
#    #    genBFinal = dict_charts['genBFinal']
#    horizon = dict_data["horizon"]
#    #    numAreas = dict_data["numAreas"]
#    #    volData = dict_data["volData"]
#    #    thermalData = dict_data["thermalData"]
#    #    battData = dict_data["battData"]
#    
#    import datetime
#    axisfixlow = horizon[0] + datetime.timedelta(hours = -360)
#    axisfixhig = horizon[stages-1] + datetime.timedelta(hours = 360)
#    x=horizon#list(range(1,stages+1))
#    
#    
#    import plotly
#    import plotly.graph_objs as go
#    
#    dict_fig ={}
#    
#    # Add data
#    #x = ['hora1', 'hora2', 'hora3', 'hora4', 'hora5', 'hora6', 'hora7', 'hora8', 'hora9',
#    #     'hora10', 'hora11', 'hora12', 'hora13', 'hora14', 'hora15', 'hora16', 'hora17', 'hora18',
#    #     'hora19', 'hora20', 'hora21', 'hora22', 'hora23', 'hora24']
#    
#    
#    trace1 = go.Bar(
#        x=x,
#        y=vecdata[0],
#        name='Modo promedio',
#        marker=dict(
#            color='rgb(8,48,107)'
#        )
#    )
#    trace2 = go.Bar(
#        x=x,
#        y=vecdata[2],
#        name='Modo variable',
#        marker=dict(
#            color='rgb(158,202,225)'
#        )
#    )
#    
#    data = [trace1, trace2]
#    layout = go.Layout(
#        title='US Export of Plastic Scrap',
#        xaxis=dict(
#            tickfont=dict(
#                size=14,
#                color='rgb(107, 107, 107)'
#            )
#        ),
#        yaxis=dict(
#            title='USD (millions)',
#            titlefont=dict(
#                size=16,
#                color='rgb(107, 107, 107)'
#            ),
#            tickfont=dict(
#                size=14,
#                color='rgb(107, 107, 107)'
#            )
#        ),
#        legend=dict(
#            x=0,
#            y=1.0,
#            bgcolor='rgba(255, 255, 255, 0)',
#            bordercolor='rgba(255, 255, 255, 0)'
#        ),
#        barmode='group',
#        bargap=0.15,
#        bargroupgap=0.1
#    )
#    
#    # Edit the layout
#    layout = dict(
#            autosize=False,
#            width=1100,
#            height=500,
#            #title = 'Variabilidad de la velocidad del viento',
#            #xaxis = dict(title = 'Month'),
#            yaxis = dict(title = 'Energía [MWh]'),
#                  )
#    
#    #fig = dict(data=data, layout=layout)
#    #py.iplot(fig, filename='styled-line')
#    fig = go.Figure(data=data, layout=layout)
#    dict_fig["aggr"] = plotly.offline.plot(fig, output_type = 'div')
#    
#    
#    from jinja2 import Environment, FileSystemLoader
#    
#    env = Environment(loader=FileSystemLoader('.'))
#    template = env.get_template("template_report8.html")
#    
#    template_vars = {"title" : "Report",
#                     "data1": "Each area dispatch",
#                     "div_placeholder1A": dict_fig["aggr"]
#                     #"div_placeholder1B": dict_fig["string2"],
#                     #"div_placeholder1C": dict_fig["string3"],
#                     #"div_placeholder1D": dict_fig["string4"],
#                     #"div_placeholder1E": dict_fig["string5"],
#                     #"data2": "All areas",
#                     #"div_placeholder2": graf3,
#                     #"data3": ,
#                     #"div_placeholder3": ,
#                     #"data4": ,
#                     #"div_placeholder4": 
#                     }
#    
#    html_out = template.render(template_vars)
#    
#    Html_file= open("results/results_report8.html","w")
#    Html_file.write(html_out)
#    Html_file.close()
#    
