def marginalcost(Param):
    
    import pickle
    dict_data = pickle.load( open( "savedata/data_save.p", "rb" ) )
    
    import csv
    #import pickle
    import openpyxl
    from utils.readxlxs import xlxstocsvres
    
    scenarios = Param.seriesForw
    stages = Param.stages-Param.bnd_stages
    
    horizon = dict_data["horizon"]
    numAreas = dict_data["numAreas"]
    
    # Historical data wind
    dict_fig ={}
    
    importedfile = openpyxl.load_workbook('results/General_results.xlsx', read_only = True, keep_vba = False)
    tabnames = importedfile.sheetnames
       
    xlxstocsvres(tabnames,'MarginalArea',importedfile)
            
    with open('results/csv_variables/'+'MarginalArea'+'.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        singleData = [[] for x in range(numAreas)]  
        for row in readCSV:
            for col in range(numAreas):
                val = row[col+1]
                try: 
                    val = float(val)
                except ValueError:
                    pass
                singleData[col].append(val)
    
    import datetime
    axisfixlow = horizon[0] + datetime.timedelta(hours = -360)
    axisfixhig = horizon[stages-1] + datetime.timedelta(hours = 360)
    x=horizon #list(range(1,stages+1))
    # x_rev = x[::-1]
    
    xlxstocsvres(tabnames,'MarginalCost',importedfile)
    
    with open('results/csv_variables/'+'MarginalCost'+'.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        maxData = [[] for x in range(numAreas)] 
        minData = [[] for x in range(numAreas)] 
        Data = [[] for x in range(numAreas)]
        
        for row in readCSV:
            for col in range(numAreas):
                auxval = []
                for k in range(scenarios):
                    val = row[(k+1)+(col+1)*scenarios-scenarios]
                    try: 
                        val = float(val)
                    except ValueError:
                        pass
                    auxval.append(val)
                Data[col].append(auxval)
                
        for col in range(numAreas):
            for stage in range(stages):
                maxData[col].append(max(Data[col][stage+3])) 
                minData[col].append(min(Data[col][stage+3]))
        
    ############################################################################
    
    import plotly 
    import plotly.graph_objs as go
    
    data = []
    
    for i in range(numAreas):
    
        # Create traces
        trace = go.Scatter(
            x = x,
            y = singleData[i][2:],
            mode = 'lines',
            name = singleData[i][1]
        )
        data.append(trace)
    
    layout = go.Layout(
    autosize=False,
    width=1000,
    height=500,
    #title='Double Y Axis Example',
    yaxis=dict(title=' Marginal cost [$/MWh]',
               titlefont=dict(
                       family='Arial, sans-serif',
                       size=18,
                       color='darkgrey'),
               #tickformat = ".0f"
               exponentformat = "e",
               #showexponent = "none",
               ticks = "inside",
               #range=[20,100]
               ),
    xaxis=dict(range=[axisfixlow,axisfixhig])
    )
               
    fig = go.Figure(data=data, layout=layout)
    dict_fig["aggr"] = plotly.offline.plot(fig, output_type = 'div')
    
    ###########################################################################
        
    from jinja2 import Environment, FileSystemLoader
    
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("templates/marginalcost_report.html")
    
    template_vars = {"title" : "Report",
                     "data1": "Each area dispatch",
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
    
    Html_file= open("results/report_variables/marginalcost_report.html","w")
    Html_file.write(html_out)
    Html_file.close()
    
    return minData

    ###########################################################################
    
def emissions(Param):
    
    # load results
    import pickle

    dict_data = pickle.load( open( "savedata/data_save.p", "rb" ) )
    dict_results = pickle.load( open( "savedata/results_save.p", "rb" ) )
    
    stages = Param.stages-Param.bnd_stages
    horizon = dict_data["horizon"]
    emsscurve = dict_results["emsscurve"]
    scenarios = Param.seriesForw
    
    # emissions curve
    dict_fig ={}
    
    import datetime
    axisfixlow = horizon[0] + datetime.timedelta(hours = -360)
    axisfixhig = horizon[stages-1] + datetime.timedelta(hours = 360)
    x=horizon #list(range(1,stages+1))
    # x_rev = x[::-1]
    
    import plotly 
    import plotly.graph_objs as go
    
    curve = []
    for i in range(stages):
        valem = 0
        for j in range(scenarios):
            valem += sum(emsscurve[j][i])
        curve.append(valem/(scenarios*1000000))
    
    # Create traces
    trace = go.Scatter(
        x = x,
        y = curve,
        mode = 'lines',
        name = 'emissions'
    )
    
    layout = go.Layout(
    autosize=False,
    width=1000,
    height=500,
    #title='Double Y Axis Example',
    yaxis=dict(title=' Millones Ton CO2 eq',
               titlefont=dict(
                       family='Arial, sans-serif',
                       size=18,
                       color='darkgrey'),
               #tickformat = ".0f"
               exponentformat = "e",
               #showexponent = "none",
               ticks = "inside",
               #range=[20,100]
               ),
    xaxis=dict(range=[axisfixlow,axisfixhig])
    )
               
    fig = go.Figure(data=[trace], layout=layout)
    dict_fig["aggr"] = plotly.offline.plot(fig, output_type = 'div')
    
    ###########################################################################
        
    from jinja2 import Environment, FileSystemLoader
    
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("templates/emissions_report.html")
    
    template_vars = {"title" : "Report",
                     "data1": "Each area dispatch",
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
    
    Html_file= open("results/report_variables/emissions_report.html","w")
    Html_file.write(html_out)
    Html_file.close()
