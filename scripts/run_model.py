def execution(Param, file):

    from scripts import main_model
    import sys
    
    # read data
    if Param.read_data is True:
        try:
            main_model.data(file)
        except IOError as e:
            sys.exit("READING DATA ERROR _ I/O error({0}): {1}".format(e.errno, e.strerror))
        except ValueError:
            sys.exit("Could not convert data")
        except:
            sys.exit("Unexpected error:", sys.exc_info()[0])
        
    # data consistency
    try:    
        main_model.data_consistency(Param)
    except IOError as e:
        sys.exit("CONSISTENCY DATA ERROR _ I/O error({0}): {1}".format(e.errno, e.strerror))
    except ValueError:
        sys.exit("Could not convert data")
    except:
        sys.exit("Unexpected error:", sys.exc_info()[0])
    
    # parameters calculation
    try:    
        main_model.parameters(Param)
    except IOError as e:
        sys.exit("PARAMETERS CALCULATION ERROR _ I/O error({0}): {1}".format(e.errno, e.strerror))
    except ValueError:
        sys.exit("Could not convert data")
    except:
        sys.exit("Unexpected error:", sys.exc_info()[0])
    
    # opf pawer flow
    try:
        main_model.grid(Param.param_opf, Param.stages)
    except IOError as e:
        sys.exit("POWER FLOW ERROR _ I/O error({0}): {1}".format(e.errno, e.strerror))
    except ValueError:
        sys.exit("Could not convert data")
    except:
        sys.exit("Unexpected error:", sys.exc_info()[0])
    
    # wind model 2 execution
    try:    
        main_model.wmodel2(Param.wind_model2, Param.stages, Param.seriesBack)
    except IOError as e:
        sys.exit("WIND MODEL 2 ERROR _ I/O error({0}): {1}".format(e.errno, e.strerror))
    except ValueError:
        sys.exit("Could not convert data")
    except:
        sys.exit("Unexpected error:", sys.exc_info()[0])
    
    # optimization module
    try:
        main_model.optimization(Param)
    except IOError as e:
        sys.exit("OPTIMIZATION ERROR _ I/O error({0}): {1}".format(e.errno, e.strerror))
    except ValueError:
        sys.exit("Could not convert data")
    except:
        sys.exit("Unexpected error:", sys.exc_info()[0])


