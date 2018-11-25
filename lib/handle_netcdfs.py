import os
import datetime
import netCDF4


def handle_netcdf_scheme_wrf(var_names, file_name, run, model, st):


    # try:

        if os.path.exists(file_name):

            data_list = []

            file = netCDF4.Dataset(file_name)
            var1 = file.variables[var_names[0]][:]
            var2 = file.variables[var_names[1]][:]
            times = file.variables["Times"][:].astype("str")
            var_latlon = (file.variables["XLAT"][0, :, :],
                          file.variables["XLONG"][0, :, :])
            file.close()

            # file de log
            log = open(st["ensemble_log_directory"][0] +
                       "Loaded_%s_%s.log" %
                       (model, run.strftime("%Y%m%d%H")), 'w')

            for t in range(times.shape[0]):
                var_date = datetime.datetime.strptime(
                    "".join(list(times[t])), "%Y-%m-%d_%H:00:00")

                if var_date <= (st['run'][0] +
                                datetime.
                                timedelta(hours=int(st['hours_ensemble'][0]))):
                    var_value = var1[t, :, :] + var2[t, :, :]
                    accumulation = t

                    if t == 0:
                        data_list.append((model,
                                          run,
                                          var_date,
                                          (var_value, accumulation),
                                          "latlon", var_latlon))
                    else:
                        data_list.append((model,
                                          run,
                                          var_date,
                                          (var_value, accumulation)))

                    log.write("run: %s --- Data: %s --- file: %s \n" %
                              (run.strftime("%Y%m%d%H"),
                               var_date.strftime("%Y%m%d%H"), file_name))

            log.close()
            return data_list

    # except:
    #    return None
