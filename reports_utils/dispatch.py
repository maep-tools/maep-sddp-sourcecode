def gendispatch(Param):
    
    import pickle
    dict_charts = pickle.load( open( "savedata/html_save.p", "rb" ) )
    dict_data = pickle.load( open( "savedata/data_save.p", "rb" ) )
    
    import plotly
    import plotly.graph_objs as go
    
    genHFinal = dict_charts['genHFinal']
    genTFinal = dict_charts['genTFinal']
    genSFinal = dict_charts['genSFinal']
    genWFinal = dict_charts['genWFinal']
    genDFinal = dict_charts['genDFinal']
    genBFinal = dict_charts['genBFinal']
    genRnFinal = dict_charts['genRnFinal']
    horizon = dict_data["horizon"]
    areasname = dict_data["areasData"][0]
    numAreas = dict_data["numAreas"]
    volData = dict_data["volData"]
    thermalData = dict_data["thermalData"]
    smallData = dict_data["smallData"]
    battData = dict_data["battData"]
    
    scenarios = Param.seriesForw
    stages = Param.stages-Param.bnd_stages
    
    import datetime
    axisfixlow = horizon[0] + datetime.timedelta(hours = -360)
    axisfixhig = horizon[stages-1] + datetime.timedelta(hours = 360)
    x=horizon #list(range(1,stages+1))
    
    ###########################################################################
    
    # all areas dispatch
    dict_fig ={}
    for z in range(numAreas):
        
        if Param.dist_free is True:
            y0_org = []
            for j in range(stages):
                val_scn = 0
                for i in range(scenarios):
                    val_scn += genRnFinal[j][z][i]
                y0_org.append(val_scn/scenarios)
        else:
            y0_org = []
            for j in range(stages):
                val_scn = 0
                for i in range(scenarios):
                    val_scn += genWFinal[j][z][i]
                y0_org.append(val_scn/scenarios)
            
        y1_org = []
        for j in range(stages):
            val_stg = 0
            for k in range(len(genBFinal[j])):
                val_scn = 0
                if battData[9][k] == z+1:
                    for i in range(scenarios):
                        val_scn += genBFinal[j][k][i]
                val_stg += val_scn/scenarios
            y1_org.append(val_stg) 
            
        y2_org = []
        for j in range(stages):
            val_stg = 0
            for k in range(len(genSFinal[j])):
                val_scn = 0
                if smallData[3][k] == z+1:
                    for i in range(scenarios):
                        val_scn += genSFinal[j][k][i]
                val_stg += val_scn/scenarios
            y2_org.append(val_stg)
            
        y3_org = []
        for j in range(stages):
            val_stg = 0
            for k in range(len(genHFinal[j])):
                val_scn = 0
                if volData[11][k] == z+1:
                    for i in range(scenarios):
                        val_scn += genHFinal[j][k][i]
                val_stg += val_scn/scenarios
            y3_org.append(val_stg)
        
        y4_org = []
        for j in range(stages):
            val_stg = 0
            for k in range(len(genTFinal[j])):
                val_scn = 0
                if thermalData[3][k] == z+1:
                    for i in range(scenarios):
                        val_scn += genTFinal[j][k][i]
                val_stg += val_scn/scenarios
            y4_org.append(val_stg)
    
        y5_org = []
        for j in range(stages):
            val_scn = 0
            for i in range(scenarios):
                val_scn += genDFinal[j][z][i]
            y5_org.append(val_scn/scenarios)
               
        # Add data to create cumulative stacked values
        y0_stck=y0_org
        y1_stck=[y0+y1 for y0, y1 in zip(y0_org, y1_org)]
        y2_stck=[y0+y1+y2 for y0, y1, y2 in zip(y0_org, y1_org, y2_org)]
        y3_stck=[y0+y1+y2+y3 for y0, y1, y2, y3 in zip(y0_org, y1_org, y2_org, y3_org)]
        y4_stck=[y0+y1+y2+y3+y4 for y0, y1, y2, y3, y4 in zip(y0_org, y1_org, y2_org, y3_org, y4_org)]
        y5_stck=[y0+y1+y2+y3+y4+y5 for y0, y1, y2, y3, y4, y5 in zip(y0_org, y1_org, y2_org, y3_org, y4_org, y5_org)]
        
        # Make original values strings and add % for hover text
        y0_txt=[str("{0:.2f}".format(y0/1000))+' GWh' for y0 in y0_org]
        y1_txt=[str("{0:.2f}".format(y1/1000))+' GWh' for y1 in y1_org]
        y2_txt=[str("{0:.2f}".format(y2/1000))+' GWh' for y2 in y2_org]
        y3_txt=[str("{0:.2f}".format(y3/1000))+' GWh' for y3 in y3_org]
        y4_txt=[str("{0:.2f}".format(y4/1000))+' GWh' for y4 in y4_org]
        y5_txt=[str("{0:.2f}".format(y5/1000))+' GWh' for y5 in y5_org]
        
        if Param.dist_free is True:
            Wind = go.Scatter(
                x=x,
                y=y0_stck,
                text=y0_txt,
                hoverinfo='x+text',
                mode='lines',
                line=dict(width=0.5,
                          color='rgb(224,243,248)'),
                fill='tonexty',
                name='Renewables'
            )
        else:
            Wind = go.Scatter(
                x=x,
                y=y0_stck,
                text=y0_txt,
                hoverinfo='x+text',
                mode='lines',
                line=dict(width=0.5,
                          color='rgb(224,243,248)'),
                fill='tonexty',
                name='Wind'
            )
                
        Batteries = go.Scatter(
            x=x,
            y=y1_stck,
            text=y1_txt,
            hoverinfo='x+text',
            mode='lines',
            line=dict(width=0.5,
                      color='rgb(111, 231, 219)'
                      ),
            fill='tonexty',
            name='Batteries'
        )
        Small = go.Scatter(
            x=x,
            y=y2_stck,
            text=y2_txt,
            hoverinfo='x+text',
            mode='lines',
            line=dict(width=0.5,
                      color='rgb(215,98,50)'
                      ),
            fill='tonexty',
            name='Small Plants'
        )
        Hydro = go.Scatter(
            x=x,
            y=y3_stck,
            text=y3_txt,
            hoverinfo='x+text',
            mode='lines',
            line=dict(width=0.5,
                      color='rgb(69,117,180)'
                      ),
            fill='tonexty',
            name='Hydro'
        )
        Thermal = go.Scatter(
            x=x,
            y=y4_stck,
            text=y4_txt,
            hoverinfo='x+text',
            mode='lines',
            line=dict(width=0.5,
                      color='rgb(215,48,39)'
                      ),
            fill='tonexty',
            name='Thermal'
        )
        
        Deficit = go.Scatter(
            x=x,
            y=y5_stck,
            text=y5_txt,
            hoverinfo='x+text',
            mode='lines',
            line=dict(width=0.5,
                      color='rgb(131, 90, 241)'
                      ),
            fill='tonexty',
            name='Deficit'
        )
        data = [Wind, Batteries, Small, Hydro, Thermal, Deficit]#, Thermal, Hydro, Small, Batteries, Wind]
        layout = go.Layout(
        autosize=False,
        width=800,
        height=500,
        title='Subsystem '+areasname[z],
        #showlegend=False,
        yaxis=dict(title='Energy [MWh]',
                   titlefont=dict(
                           family='Arial, sans-serif',
                           size=18,
                           color='darkgrey'),
                   #tickformat = ".0f"
                   exponentformat = "e",
                   #showexponent = "none",
                   ticks = "inside"
                   ),
        xaxis=dict(range=[axisfixlow,axisfixhig])
        )
        
        fig = go.Figure(data=data, layout=layout)
        # plotly.offline.plot(fig, filename='stacked-area-plot-hover', output_type = 'div')
        dict_fig["string{0}".format(z+1)] = plotly.offline.plot(fig, output_type = 'div')
        
    ###########################################################################
    
    # each areas dispatch
    if Param.dist_free is True:
        y0_org = []
        for j in range(stages):
            val_stg = 0
            for k in range(len(genRnFinal[j])):
                val_scn = 0
                for i in range(scenarios):
                    val_scn += genRnFinal[j][k][i]
                val_stg += val_scn/scenarios
            y0_org.append(val_stg)
    else:
        y0_org = []
        for j in range(stages):
            val_stg = 0
            for k in range(len(genWFinal[j])):
                val_scn = 0
                for i in range(scenarios):
                    val_scn += genWFinal[j][k][i]
                val_stg += val_scn/scenarios
            y0_org.append(val_stg)
            
    y1_org = []
    for j in range(stages):
        val_stg = 0
        for k in range(len(genBFinal[j])):
            val_scn = 0
            for i in range(scenarios):
                val_scn += genBFinal[j][k][i]
            val_stg += val_scn/scenarios
        y1_org.append(val_stg) 
    
    y2_org = []
    for j in range(stages):
        val_stg = 0
        for k in range(len(genSFinal[j])):
            val_scn = 0
            for i in range(scenarios):
                val_scn += genSFinal[j][k][i]
            val_stg += val_scn/scenarios
        y2_org.append(val_stg)
        
    y3_org = []
    for j in range(stages):
        val_stg = 0
        for k in range(len(genHFinal[j])):
            val_scn = 0
            for i in range(scenarios):
                val_scn += genHFinal[j][k][i]
            val_stg += val_scn/scenarios
        y3_org.append(val_stg)
    
    y4_org = []
    for j in range(stages):
        val_stg = 0
        for k in range(len(genTFinal[j])):
            val_scn = 0
            for i in range(scenarios):
                val_scn += genTFinal[j][k][i]
            val_stg += val_scn/scenarios
        y4_org.append(val_stg)

    y5_org = []
    for j in range(stages):
        val_stg = 0
        for k in range(len(genDFinal[j])):
            val_scn = 0
            for i in range(scenarios):
                val_scn += genDFinal[j][k][i]
            val_stg += val_scn/scenarios
        y5_org.append(val_stg)
           
    # Add data to create cumulative stacked values
    y0_stck=y0_org
    y1_stck=[y0+y1 for y0, y1 in zip(y0_org, y1_org)]
    y2_stck=[y0+y1+y2 for y0, y1, y2 in zip(y0_org, y1_org, y2_org)]
    y3_stck=[y0+y1+y2+y3 for y0, y1, y2, y3 in zip(y0_org, y1_org, y2_org, y3_org)]
    y4_stck=[y0+y1+y2+y3+y4 for y0, y1, y2, y3, y4 in zip(y0_org, y1_org, y2_org, y3_org, y4_org)]
    y5_stck=[y0+y1+y2+y3+y4+y5 for y0, y1, y2, y3, y4, y5 in zip(y0_org, y1_org, y2_org, y3_org, y4_org, y5_org)]
    
    # Make original values strings and add % for hover text
    y0_txt=[str("{0:.2f}".format(y0/1000))+' GWh' for y0 in y0_org]
    y1_txt=[str("{0:.2f}".format(y1/1000))+' GWh' for y1 in y1_org]
    y2_txt=[str("{0:.2f}".format(y2/1000))+' GWh' for y2 in y2_org]
    y3_txt=[str("{0:.2f}".format(y3/1000))+' GWh' for y3 in y3_org]
    y4_txt=[str("{0:.2f}".format(y4/1000))+' GWh' for y4 in y4_org]
    y5_txt=[str("{0:.2f}".format(y5/1000))+' GWh' for y5 in y5_org]
    
    if Param.dist_free is True:
        Wind = go.Scatter(
            x=x,
            y=y0_stck,
            text=y0_txt,
            hoverinfo='x+text',
            mode='lines',
            line=dict(width=0.5,
                      color='rgb(224,243,248)'),
            fill='tonexty',
            name='Wind'
        )
    else:
        Wind = go.Scatter(
            x=x,
            y=y0_stck,
            text=y0_txt,
            hoverinfo='x+text',
            mode='lines',
            line=dict(width=0.5,
                      color='rgb(224,243,248)'),
            fill='tonexty',
            name='Renewables'
        )
            
    Batteries = go.Scatter(
        x=x,
        y=y1_stck,
        text=y1_txt,
        hoverinfo='x+text',
        mode='lines',
        line=dict(width=0.5,
                  color='rgb(111, 231, 219)'),
        fill='tonexty',
        name='Batteries'
    )
    Small = go.Scatter(
        x=x,
        y=y2_stck,
        text=y2_txt,
        hoverinfo='x+text',
        mode='lines',
        line=dict(width=0.5,
                  color='rgb(215,98,50)'
                  ),
        fill='tonexty',
        name='Small Plants'
    )    
    Hydro = go.Scatter(
        x=x,
        y=y3_stck,
        text=y3_txt,
        hoverinfo='x+text',
        mode='lines',
        line=dict(width=0.5,
                  color='rgb(69,117,180)'),
        fill='tonexty',
        name='Hydro'
    )
    Thermal = go.Scatter(
        x=x,
        y=y4_stck,
        text=y4_txt,
        hoverinfo='x+text',
        mode='lines',
        line=dict(width=0.5,
                  color='rgb(215,48,39)'),
        fill='tonexty',
        name='Thermal'
    )
   
    Deficit = go.Scatter(
        x=x,
        y=y5_stck,
        text=y5_txt,
        hoverinfo='x+text',
        mode='lines',
        line=dict(width=0.5,
                  color='rgb(131, 90, 241)'),
        fill='tonexty',
        name='Deficit'
    )
    data = [Wind, Batteries, Small, Hydro, Thermal, Deficit]#Deficit, Thermal, Hydro, Small, Batteries, Wind]
    layout = go.Layout(
    autosize=False,
    width=800,
    height=500,
    #title='Double Y Axis Example',
    yaxis=dict(title='Energy [MWh]',
               titlefont=dict(
                       family='Arial, sans-serif',
                       size=18,
                       color='darkgrey'),
               #tickformat = ".0f"
               exponentformat = "e",
               #showexponent = "none",
               ticks = "inside"
               ),
    xaxis=dict(range=[axisfixlow,axisfixhig])
    )
    #layout = go.Layout(showlegend=False)
    fig = go.Figure(data=data, layout=layout)
    # plotly.offline.plot(fig, filename='stacked-area-plot-hover', output_type = 'div')
    graf3 = plotly.offline.plot(fig, output_type = 'div')
    
    ###########################################################################
    
    from jinja2 import Environment, FileSystemLoader
    
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("templates/areasdispatch_report.html")
    
    template_vars = {"title" : "Report",
                     "data1": "Each area dispatch",
                     "div_placeholder1": [],
                     "div_placeholder2": [],
                     "div_placeholder3": [],
                     "div_placeholder4": [],
                     "div_placeholder5": [],
                     "div_placeholder6": [],
                     "div_placeholder7": [],
                     "div_placeholder8": [],
                     "div_placeholder9": [],
                     "div_placeholder10": [],
                     "div_placeholder11": [],
                     "div_placeholder12": [],
                     "div_placeholder13": [],
                     "div_placeholder14": [],
                     "div_placeholder15": [],
                     "div_placeholder16": [],
                     "div_placeholder17": [],
                     "div_placeholder18": [],
                     "div_placeholder19": [],
                     "div_placeholder20": [],
                     "div_placeholder21": [],
                     "data2": "All areas",
                     "div_placeholder22": [],
                     }
    
    template_vars['div_placeholder22']=graf3
    
    for z in range(numAreas):
        template_vars['div_placeholder'+str(z+1)]=dict_fig['string'+str(z+1)]
    
    html_out = template.render(template_vars)
    
    Html_file= open("results/areasdispatch_report.html","w")
    Html_file.write(html_out)
    Html_file.close()

    ###########################################################################

def genrenewables(Param): 
    
    import pickle
    dict_charts = pickle.load( open( "savedata/html_save.p", "rb" ) )
    dict_data = pickle.load( open( "savedata/data_save.p", "rb" ) )
    
    # plor format
    dict_fig ={}
    
    import plotly
    import plotly.graph_objs as go

    genWFinal = dict_charts['genWFinal']
    genRnFinal = dict_charts['genRnFinal']
    horizon = dict_data["horizon"]
    
    scenarios = Param.seriesForw
    stages = Param.stages-Param.bnd_stages
    
    import datetime
    axisfixlow = horizon[0] + datetime.timedelta(hours = -360)
    axisfixhig = horizon[stages-1] + datetime.timedelta(hours = 360)
    x=horizon #list(range(1,stages+1))
    
    ###########################################################################
    
    # all areas dispatch
    if Param.dist_free is True:
        y0_org = []
        for j in range(stages):
            val_stg = 0
            for k in range(len(genRnFinal[j])):
                val_scn = 0
                for i in range(scenarios):
                    val_scn += genRnFinal[j][k][i]
                val_stg += val_scn/scenarios
            y0_org.append(val_stg)
        
    else:
        y0_org = []
        for j in range(stages):
            val_stg = 0
            for k in range(len(genWFinal[j])):
                val_scn = 0
                for i in range(scenarios):
                    val_scn += genWFinal[j][k][i]
                val_stg += val_scn/scenarios
            y0_org.append(val_stg)
    
    
    # Create traces
    trace = go.Scatter(
            x = x[:30],
            y = y0_org[:],
            mode = 'lines',
            name = 'renewables dispatch'
        )
            
    data = [trace]
    layout = go.Layout(
    autosize=False,
    width=800,
    height=500,
    #title='Double Y Axis Example',
    yaxis=dict(title='Energy [MWh]',
               titlefont=dict(
                       family='Arial, sans-serif',
                       size=18,
                       color='darkgrey'),
               #tickformat = ".0f"
               exponentformat = "e",
               #showexponent = "none",
               ticks = "inside"
               ),
    xaxis=dict(range=[axisfixlow,axisfixhig])
    )
    fig = go.Figure(data=data, layout=layout)
    dict_fig["aggr"] = plotly.offline.plot(fig, output_type = 'div')
    
    from jinja2 import Environment, FileSystemLoader
    
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("templates/renewables_report.html")
    
    template_vars = {"title" : "Report",
                     "data1": "Renewables dispatch",
                     "div_placeholder1A": dict_fig["aggr"]
                     }
    
    html_out = template.render(template_vars)
    
    Html_file= open("results/report_variables/renewables_report.html","w")
    Html_file.write(html_out)
    Html_file.close()
    