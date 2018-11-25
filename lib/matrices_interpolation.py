import matplotlib.mlab
import multiprocessing
import lib.parallelization
import lib.list_and_dictionary


def interpolate_matrix(args):

    model = args[0][0]
    run = args[0][1]
    data = args[0][2]
    # st = args[1]
    ensemble_data = args[2]
    target_lat = args[3]
    target_lon = args[4]
    ensemble_data_tmp = args[5]

    Nlat = ensemble_data[model][run]['latlon'][0].shape[0]
    Nlon = ensemble_data[model][run]['latlon'][0].shape[1]

    interpolated_matrix = matplotlib.mlab.griddata(
        ensemble_data[model][run]['latlon'][1].reshape(Nlat * Nlon),
        ensemble_data[model][run]['latlon'][0].reshape(Nlat * Nlon),
        ensemble_data[model][run][data].reshape(Nlat * Nlon),
        target_lon, target_lat, interp="linear")

    ensemble_data_tmp.append((model, run, data, interpolated_matrix))


def matrices_interpolation(st, ensemble_data, target_lat, target_lon,
                           interpolated_data):

    # files with interpolated data
    interpolated_files = list(interpolated_data.ensemble_interp_data.keys())
    interpolated_files.sort()
    interpolated_files = interpolated_files[::-1]

    # duplicated for now
    ensemble_data_tmp_parallel = multiprocessing.Manager().list()
    ensemble_data_tmp = []

    for m in ensemble_data.keys():
        for r in ensemble_data[m].keys():

            processes_temp = []
            dates = list(ensemble_data[m][r].keys())
            dates.remove('latlon')
            dates.sort()
            for d in dates:

                processes_temp.append((m, r, d))

                # Check if exists interpolated data for the triple
                # (m, r, d)
                # if yes then remove the interpolation process
                for f in interpolated_files:
                    if m in interpolated_data.ensemble_interp_data[f].keys():
                        if r in interpolated_data.ensemble_interp_data[f][m].keys():
                            if d in interpolated_data.ensemble_interp_data[f][m][r].keys():
                                
                                try:

                                    processes_temp.remove((m, r, d))
                                                                  
                                    #print("Interpolated matrix for Model: %s, Run: %s, Date: %s" %
                                    #      (m, r.strftime("%Y/%m/%d %H"), d.strftime("%Y/%m/%d %H")))
                               
                                    ensemble_data_tmp.append((m, r, d, interpolated_data.ensemble_interp_data[f][m][r][d]))
                                except ValueError:
                                    pass

            lib.parallelization.processes_in_parallel(
                int(st["interpolations_in_parallel"][0]),
                processes_temp, interpolate_matrix,
                [st, ensemble_data, target_lat, target_lon,
                 ensemble_data_tmp_parallel])

    ensemble_data_tmp.extend(ensemble_data_tmp_parallel)
    ensemble_data = lib.list_and_dictionary.list_to_dict(ensemble_data_tmp)

    del interpolated_data.ensemble_interp_data
    del ensemble_data_tmp
    del ensemble_data_tmp_parallel

    return ensemble_data
