def inputhydro(dict_data):
    
    import pickle
    dict_sim = pickle.load( open( "savedata/format_sim_save.p", "rb" ) )
    
    yearvec = dict_sim['yearvector']
    biomassPlants = dict_data['BiomassPlants']
    biomassData = dict_data['BiomassData']
    
    # hydro limits
    numStock = len(biomassPlants) # Reservoirs asociated with biomass power plants

    