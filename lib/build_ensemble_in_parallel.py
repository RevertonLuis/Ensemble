import os
import netCDF4
import numpy
import time
import lib.weighted
import multiprocessing
import ctypes
import math

# Number of processors to compute the statistics in parallel
processors_number = 24 #multiprocessing.cpu_count()

def run_processes_in_parallel(number_of_processes,
                              processes_load,
                              method,
                              arguments):

    # Processes list
    processes = []
      
    # Load of each cpu
    load = int(math.ceil(float(len(processes_load))/number_of_processes))

    # For each cpu
    for p in range(number_of_processes):

       # List of loads for each processes
       cpu_loads = processes_load[p*load:(p+1)*load]

       # Add the process in the processes list
       processes.append(multiprocessing.Process(target=method,
                                                args=(cpu_loads,
                                                      arguments[0],
                                                      arguments[1], 
                                                      arguments[2],
                                                      arguments[3],
                                                      arguments[4],
                                                      arguments[5],)))
    
    # Running the processes
    for process in processes:
    
       # start each process in parallel 
       process.start()

    # "blocking" the processes
    for process in processes:
    
       # wait for all cpus finish their jobs
       process.join()

def weighted_percentile(j, i, q, matrices_c, weights,
                        weight_matrices):

    return (lib.weighted.quantile(matrices_c[:, j, i], 
                                  weights * 
                                  weight_matrices[:, j, i], q))

def weighted_mean(j, i, q, matrices_c, weights, weight_matrices):
   
    # Remark: this function don't use q
    return numpy.average(matrices_c[:, j, i], weights=(weights * 
                                              weight_matrices[:, j, i]))

def compute_statistic_in_parallel(cpu_loads, st, dates, ensemble, 
                                  weights, weight_matrices, shared_matrix):

    # for each statistic
    for statistic, si in zip(st["statistics"],
                             range(len(st["statistics"]))):

        stat_func = weighted_mean
        q = None
        if statistic not in ["mean", "linear_combination"]:
            stat_func = weighted_percentile
            q = float(st["statistic_%s" % statistic][1])

        # For each date
        for date, di in zip(dates, range(len(dates))):

            for load in cpu_loads:
                j, i = load
                shared_matrix[si, di, j, i] = stat_func(j, i, q, ensemble[date],
                                                        weights[date],
                                                        weight_matrices[date])

def run_in_parallel(st, dates, target_grid, 
                    ensemble, weights, weight_matrices):

    Nj, Ni = target_grid.lat.shape
    Nt = len(dates)
    Ns = len(st["statistics"])

    # ---------- Remark ------------------
    # In the future change this load
    # to be close area squares, that is,
    # list of 
    # [j_start, j_ent, i_start, i_end] for
    # each processor
    # instead of
    # a list of pairs (j,i)
    cpu_loads = []
    for j in range(Nj):
        for i in range(Ni):
            cpu_loads.append((j, i))
    # ------------------------------------

    shared_array_base = multiprocessing.Array(ctypes.c_float, Ns * Nt * Nj * Ni)
    shared_matrix = numpy.ctypeslib.as_array(shared_array_base.get_obj())
    shared_matrix = shared_matrix.reshape(Ns, Nt, Nj, Ni)
    
    # Will compute the statistic in parallel
    run_processes_in_parallel(processors_number, cpu_loads,
                              compute_statistic_in_parallel,
                              [st, dates, ensemble, weights, 
                               weight_matrices, shared_matrix])

    return shared_matrix

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
        file.variables[variable].long_name = " ".join(st["statistic_%s" %
                                                         statistic][2:])
   
    file.variables["latitude"][:,:]  = lat[:,:].astype('f')
    file.variables["longitude"][:,:] = lon[:,:].astype('f')
    file.variables["latitude"].units  = 'degrees_north'
    file.variables["longitude"].units = 'degrees_east'
    file.variables["times"].units = "seconds since 1970-01-01 00:00 UTC"

    shared_matrix = run_in_parallel(st, dates, target_grid, ensemble, weights, weight_matrices)
    
    # For each date
    for date, di in zip(dates, range(len(dates))):

         date_tuple = (date.year, date.month, date.day, date.hour,
                       date.second, date.microsecond, 0, 0, 0)

         date_timestamp = time.mktime(date_tuple)

         file.variables["times"][di]  = date_timestamp

         # for each statistic
         for statistic, si in zip(st["statistics"], range(len(st["statistics"]))):
 
             variable =  st["statistic_%s" % statistic][0]
	  
             file.variables[variable][di,:,:] = shared_matrix[si, di, :, :]

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
		    
                    # Write the log line
                    line = line + "  " + "%s_%s" % (model,
                                                    run.strftime("%Y%m%d%H"))

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
