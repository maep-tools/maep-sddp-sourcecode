def chargedis(Param):
    
    import pickle
    dict_charts = pickle.load( open( "savedata/html_save.p", "rb" ) )
    
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
    
    ##########################################################################
    
# number of cycles
