def hydrogen(Param):
    
    import pickle
    dict_data = pickle.load( open( "savedata/data_save.p", "rb" ) )
    
    import csv
    
    scenarios = Param.seriesForw
    stages = Param.stages-Param.bnd_stages
    blocks = len(dict_data["blocksData"][0])
    horizon = dict_data["horizon"]
    
    # Historical data wind
    dict_fig ={}
    
    import datetime
    axisfixlow = horizon[0] + datetime.timedelta(hours = -360)
    axisfixhig = horizon[stages-1] + datetime.timedelta(hours = 360)
    x=horizon #list(range(1,stages+1))
    # x_rev = x[::-1]
    
    with open('results/csv_variables/'+'HydroGeneration'+'.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: columns = len(row); break 
    
    # Number of plants
    plants = int((columns-2)/scenarios)
    
    # saving data
    with open('results/csv_variables/'+'HydroGeneration'+'.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        plantsData = [[] for x in range(plants)] 
        
        for row in readCSV:
            for col in range(plants):
                auxval = []
                for z in range(scenarios):
                    val = row[col*scenarios+z+2]
                    try: 
                        val = float(val)
                    except ValueError:
                        pass
                    auxval.append(val)
                plantsData[col].append(auxval)
     
    # Choose the plant to draw the scenarios
    drawplant  = plantsData[Param.curves[2][1]-1]
    tray_scn = [[] for x in range(scenarios)] 
    for y in range(stages):
        val = drawplant[y*blocks+2:y*blocks+blocks+2]
        vecscen = [sum(x) for x in zip(*val)]
        for z in range(scenarios):
            tray_scn[z].append(vecscen[z])
        
    ###########################################################################
    
    import plotly 
    import plotly.graph_objs as go
    
    data = []
    
    for i in range(scenarios):
    
        # Create traces
        trace = go.Scatter(
            x = x[:stages],
            y = tray_scn[i][:],
            mode = 'lines',
            name = 'sceanrios '+str(i+1)
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
    template = env.get_template("templates/hydrogen_report.html")
    
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
    
    Html_file= open("results/report_variables/hydrogen_report.html","w")
    Html_file.write(html_out)
    Html_file.close()
