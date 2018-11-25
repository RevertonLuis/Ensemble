import os
import netCDF4
import numpy
import time
import lib.weighted

def compute_weighted_percentile(q, matrices_c, weights, weight_matrices):

    M, Nj, Ni = matrices_c.shape
    M2 = len(weights)
    
    if M != M2:
       print("Number of weights != Number of matrices")
       exit()
    else:
    
       matrix_weighted = numpy.empty( (Nj,Ni), 'f' )

       for j in range(Nj):
           for i in range(Ni):
	       
               matrix_weighted[j,i] = lib.weighted.quantile(matrices_c[:,j,i], weights * weight_matrices[:, j, i], q)
    
    return matrix_weighted

def compute_weighted_mean(matrices_c, weights, weight_matrices):

    M, Nj, Ni = matrices_c.shape
    M2 = len(weights)
    
    if M != M2:
       print("Number of weights != Number of matrices")
       exit()
    else:
    
       matrix_weighted = numpy.empty((Nj,Ni), 'f')

       for j in range(Nj):
           for i in range(Ni):
	       
               matrix_weighted[j,i] = numpy.average(matrices_c[:,j,i], weights=(weights * weight_matrices[:, j, i]))
    
    return matrix_weighted


def save_the_statistics(st, ensemble, target_grid, weights, weight_matrices):

    # With the matrices stacked is possible to compute the statistics
    #maximum          = weighted.quantile(matrices_c,   1., weights )
    #quartile_upper   = weighted.quantile(matrices_c, 0.75, weights )
    #median           = weighted.quantile(matrices_c, 0.50, weights )
    #quartile_lower   = weighted.quantile(matrices_c, 0.25, weights )
    #minimum          = weighted.quantile(matrices_c,   0., weights )

    lat = target_grid.lat
    lon = target_grid.lon

    # The dates with data
    dates = list(ensemble.keys())
    dates.sort()

    # Ensemble file 
    ensemble_file = st["ensemble_file"][0]

    # Check if the ensemble_file exists
    if os.path.exists(ensemble_file):
        os.remove(ensemble_file)

    # Open the file
    file = netCDF4.Dataset(st["run"][0].strftime(ensemble_file), 'w')
    
    file.createDimension("latitude",  lat.shape[0])
    file.createDimension("longitude", lon.shape[1])
    file.createDimension("times",     len(dates))

    file.createVariable("latitude",  'f', ("latitude", "longitude"))
    file.createVariable("longitude", 'f', ("latitude", "longitude"))
    file.createVariable("times", 'd', ("times",))

    # for each statistic create a variable
    for statistic in st["statistics"]:
        variable =  st["statistic_%s" % statistic][0]

        file.createVariable(variable, 'f', ("times",
                                            "latitude",
                                            "longitude"))
        
        # create the variable long_name
        file.variables[variable].long_nome = " ".join(st["statistic_%s" %
                                                         statistic][2:])
   
    file.variables["latitude"][:,:]  = lat[:,:].astype('f')
    file.variables["longitude"][:,:] = lon[:,:].astype('f')
    file.variables["latitude"].units  = 'degrees_north'
    file.variables["longitude"].units = 'degrees_east'
    file.variables["times"].units = "seconds since 1970-01-01 00:00 UTC"

    # For each date
    for date, index in zip(dates, range(len(dates))):

         date_tupla = (date.year, date.month, date.day, date.hour,
                       date.second, date.microsecond, 0, 0, 0)

         date_timestamp = time.mktime(date_tupla)

         file.variables["times"][index]  = date_timestamp

         # for each statistic
         for statistic in st["statistics"]:
 
             variable =  st["statistic_%s" % statistic][0]
	
             if statistic == "mean":
                 matrix = compute_weighted_mean(ensemble[date],
                                                weights[date],
                                                weight_matrices[date])

             elif statistic == "linear_combination":
                 pass
             
             else:
                 
                 matrix = compute_weighted_percentile(float(st["statistic_%s" %
                                                               statistic][1]),
                                                      ensemble[date],
                                                      weights[date],
                                                      weight_matrices[date])

             file.variables[variable][index,:,:]   = matrix[:,:].astype('f')

    try:
        # global attribs for the thredds
        setattr(file, 'GRIDTYPE',      target_grid.GRIDTYPE)
        setattr(file, 'MAP_PROJ',      target_grid.MAP_PROJ)
        setattr(file, 'CEN_LON',       target_grid.CEN_LON)
        setattr(file, 'MAP_PROJ_CHAR', target_grid.MAP_PROJ_CHAR)
        setattr(file, 'STAND_LON',     target_grid.STAND_LON)
        setattr(file, 'TRUELAT1',      target_grid.TRUELAT1)
        setattr(file, 'TRUELAT2',      target_grid.TRUELAT2)
        setattr(file, 'CEN_LAT',       target_grid.CEN_LAT)
        setattr(file, 'DX',            target_grid.DX )
        setattr(file, 'DY',            target_grid.DY)
        setattr(file, 'MOAD_CEN_LAT',  target_grid.MOAD_CEN_LAT)
    except:
        pass

    # close the file
    file.close()


def build_ensemble(st, ensemble_data, dates, target_grid):

    # write a log about the models that will compose the ensemble 
    log = (open(st["ensemble_log_directory"][0] +
           st['run'][0].strftime(st["ensemble_log_name"][0]), 'w'))

    ensemble = {}
    ensemble_weight_matrices = {}
    weights = {}

    # For each date in the ensemble
    for date in dates:

        weights[date] = []
        
        line         = "Date: %s --- Models: " % date.strftime("%Y%m%d%H")
        line_weights = "Date: %s --- Models: " % date.strftime("%Y%m%d%H")


        # Matrices that will be stacked
        matrices = []
	
	# Weight matrices that will be stacked
        weight_matrices = []

        for model in ensemble_data.keys():
            for run in ensemble_data[model].keys():
            
                # Check if the needed date is in model
                if date in ensemble_data[model][run].keys():
               
                    # will be stacked
                    matrices.append(ensemble_data[model][run][date])
		    		    
                    weight = float(st["weight_%s" % model][0])
                    weights[date].append(weight)
		    
		    # Weight matrices
                    weight_matrices.append(ensemble_data[model][run]
                                           ['weight_matrix'])
		    
                    # Escrevendo a line do log
                    # Write the log line
                    line = line + "  " + "%s_%s" % (model,
                                                    run.strftime("%Y%m%d%H"))
                    line_weights = (line_weights + "  " + "%s_%s_Peso_%f" % 
                                    (model, run.strftime("%Y%m%d%H"),
                                     weight))

        # Stacking the matrices
        if len(matrices) > 0:
            ensemble[date] = numpy.stack(matrices, axis=0)
            ensemble_weight_matrices[date] = numpy.stack(weight_matrices, axis=0)

        # write in the log
        log.write(line + "\n") 
    log.close()         
    
    if len(ensemble.keys()) > 0:

       # Save the results
       save_the_statistics(st, ensemble, target_grid, weights, ensemble_weight_matrices) 
