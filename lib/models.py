import os
import datetime
import multiprocessing

# models do projeto
import lib.parallelization
import lib.handle_gribs
import lib.handle_netcdfs
import lib.fix_accumulations
import lib.list_and_dictionary


def load_model_in_parallel(args):

    model_run = args[0]
    st = args[1]
    ensemble_data = args[2]
    models_files = args[3]

    model = model_run[0]
    run = model_run[1]
    format = st["format_file_%s" % model][0]
    directory = run.strftime(st["directory_%s" % model][0])
    acc_scheme = st["acc_scheme_%s" % model][0]

    if format.lower() == "grib":
        if acc_scheme == "GFS" or acc_scheme == "GEFS":

            var_names = " ".join(st["scheme_%s_variables" % acc_scheme])

            # log file
            log = open(st["ensemble_log_directory"][0] +
                       "loaded_%s_%s.log" %
                       (model, run.strftime("%Y%m%d%H")), 'w')

            # For each file of model and
            # run open and load the precipitation variable
            # Flag to load latlon
            latlon_flag = True
            for file in models_files[model][run]:

                (date,
                 value,
                 latlon,
                 acc) = (lib.handle_gribs.
                         handle_grib_scheme_gfs(var_names, directory + file,
                                                run, latlon_flag))

                if (date is not None and
                   date <= (st['run'][0] +
                            datetime.timedelta(
                            hours=int(st['hours_ensemble'][0])))):

                    if latlon_flag:
                        ensemble_data.append((model,
                                              run,
                                              date,
                                              (value, acc), "latlon", latlon))
                        latlon_flag = False
                    else:
                        ensemble_data.append((model,
                                              run,
                                              date,
                                              (value, acc)))

                    # write the log
                    log.write("run: %s --- Date: %s --- File: %s \n" %
                              (run.strftime("%Y%m%d%H"),
                               date.strftime("%Y%m%d%H"),
                               directory + file))

            # Close the log
            log.close()
            
        if acc_scheme == "CPTEC":

            var_names = " ".join(st["scheme_%s_variables" % acc_scheme])

            # New because of issues with
            # file.select(name="Total precipitation")
            # not working with the models BAM and BRAMS
            grib_message = int(st["scheme_%s_grib_message_%s" %
                               (acc_scheme, model)][0])

            # Log file
            log = open(st["ensemble_log_directory"][0] +
                       "Loaded_%s_%s.log" % (model,
                                             run.strftime("%Y%m%d%H")), 'w')

            # For each file of model and
            # run open and load the precipitation variable
            # Flag to load latlon
            latlon_flag = True
            for file in models_files[model][run]:

                if model == "ETA":
                    (date,
                     value,
                     latlon,
                     acc) = (lib.handle_gribs.
                             handle_grib_scheme_cptec_eta(var_names,
                                                          directory + file,
                                                          run,
                                                          latlon_flag))

                    if date is not None:

                        # ETA values must be multiplied by a
                        # factor (1000 or other defined in the
                        # settings file variable scheme_CPTEC_factor_ETA
                        value = value * float(st["scheme_CPTEC_factor_%s" %
                                              model][0])

                if model == "BRAMS" or model == "BAM":
                    (date,
                     value,
                     latlon,
                     acc) = (lib.handle_gribs.
                             handle_grib_scheme_cptec_brams_bam(grib_message,
                                                                directory +
                                                                file,
                                                                run,
                                                                latlon_flag))

                if (date is not None and
                    date <= (st['run'][0] +
                             datetime.timedelta(
                             hours=int(st['hours_ensemble'][0])))):

                    if latlon_flag:
                        ensemble_data.append((model,
                                              run,
                                              date,
                                              (value, acc), "latlon", latlon))
                        latlon_flag = False
                    else:
                        ensemble_data.append((model,
                                              run,
                                              date,
                                              (value, acc)))

                    # write the log
                    log.write("run: %s --- Data: %s --- Arquivo: %s \n" %
                              (run.strftime("%Y%m%d%H"),
                               date.strftime("%Y%m%d%H"), directory + file))

            # close the log
            log.close()

    if format.lower() == "netcdf":
        if acc_scheme == "WRF":
            var_names = st["scheme_%s_variables" % acc_scheme]
            for file in models_files[model][run]:
                data_list = (lib.handle_netcdfs.
                             handle_netcdf_scheme_wrf(var_names,
                                                      directory + file,
                                                      run,
                                                      model,
                                                      st))

                ensemble_data.extend(data_list)
                del data_list


class Models():

    def __init__(self, settings):

        self.st = settings

    def create_ensemble_dates(self):

        """ Method that create the dates for the ensemble """

        self.dates = [self.st["run"][0] +
                      datetime.timedelta(hours=h)
                      for h in range(int(self.st["hours_ensemble"][0]) + 1)]

    def check_files_availability(self):

        """ Method that checks the files availability """

        # dictionary with the available moodels
        self.models_files = {}

        for model in self.st["models"]:
            self.models_files[model] = {}

            # models run
            runs = [int(h) for h in self.st["runs_%s" % model]]

            # Gerando as runs de cada model que serao consideradas
            for run_day in range(int(self.st["days_%s" % model][0])):

                for run_hour in range(24):

                    run = (self.st["run"][0] -
                           datetime.timedelta(days=run_day, hours=run_hour))

                    if run.hour in runs:

                        # building the dictionary
                        directory = run.strftime(
                            self.st["directory_%s" % model][0])

                        if os.path.exists(directory):

                            # warning about empty directory
                            if len(os.listdir(directory)) == 0:
                                print("")
                                print("Warning: directory %s " +
                                      "associated with model %s " +
                                      "and run %s IS EMPTY" %
                                      (directory, model,
                                       run.strftime("%Y/%m/%d %H")))

                            self.models_files[model][run] = (os.
                                                             listdir(directory))

                            # ----------- deprecated in the future  -------------
                            # OBS: When the files are in a directory with the
                            # run in it's name (the directory name) the code
                            # below will be obsolete
                            # treating the models with the different runs in the
                            # same directory
                            old_list = self.models_files[model][run][:]
                            for file in old_list:

                                try:
                                    run_file = (datetime.
                                                datetime.
                                                strptime(file,
                                                         self.
                                                         st["file_name_%s" %
                                                         model][0]))
                                    if run_file == run:
                                        self.models_files[model][run] = [file]
                                except ValueError:
                                    pass
                            # ----------------------------------------------------

                            # Removing from the list files that are not models
                            # like ctls, anl, txt, busca.ok, etc
                            old_list = self.models_files[model][run][:]
                            for file in old_list:
                                if file.find(run.
                                    strftime(self.st["file_name_%s" %
                                                     model][0])) == -1:

                                    self.models_files[model][run].remove(file)

                                else:

                                    # For some models is possible to determine
                                    # the bound dates therefore load only
                                    # necessary files
                                    # upper_bound_date
                                    u_date = (self.st["run"][0] +
                                              datetime.timedelta(
                                              hours=int(self.
                                              st["hours_ensemble"][0])) +
                                              datetime.timedelta(
                                              hours=int(
                                              self.st["interp_tol"][0])))

                                    # lower_bound_date
                                    l_date = (self.st["run"][0] -
                                              datetime.timedelta(
                                              hours=int(self.st["interp_tol"][0])))

                                    date_file_now = None

                                    if model == "GFS" or model == "GEFS":

                                        date_file_now = (run +
                                                         datetime.
                                                         timedelta(hours=int(
                                                             file[-3:])))

                                    if model == "ETA":

                                        date_file_now = (datetime.datetime.strptime(
                                                         file[len(run.strftime(self.st["file_name_%s" % model][0])) + 1 : - 4], "%Y%m%d%H"))

                                    if model == "BRAMS":

                                        date_file_now = datetime.datetime.strptime(file[len(run.strftime( self.st["file_name_%s" % model][0] ) )+1:-6], "%Y%m%d%H")

                                    if model == "BAM":

                                        date_file_now = datetime.datetime.strptime(file[len(run.strftime( self.st["file_name_%s" % model][0] ) ):-7], "%Y%m%d%H")

                                    # removing all the files that are not
                                    # in the interval
                                    # lower_bound_date <= date_file_now
                                    # <= upper_bound_date
                                    if (date_file_now is not None):
                                        if ((l_date <= date_file_now) and
                                           (date_file_now <= u_date)):
                                            pass
                                        else:
                                            self.models_files[model][run].remove(file)

                        else:
                            print("")
                            print("Warning: directory %s " 
                                  "associated with model %s " 
                                   "and run %s IS EMPTY" %
                                  (directory, model,
                                  run.strftime("%Y/%m/%d %H")))
                            print("")

    def load_models(self):

        """ Method that load the models proper precipitation variables """

        # Lista temporaria para resolver o problema de atualizacao paralela
        # Temporary list to solve the issue with the parallel update of
        # multiprocessing.Manager().dict()
        ensemble_data_tmp = multiprocessing.Manager().list()

        processes_temp = []
        for model in self.models_files.keys():
            for run in self.models_files[model]:
                processes_temp.append((model, run))

        # processes_temp in parallel
        lib.parallelization.processes_in_parallel(
            int(self.st["models_in_parallel"][0]),
            processes_temp, load_model_in_parallel,
            [self.st, ensemble_data_tmp, self.models_files])

        # convert the temporary list to a dictionary
        self.ensemble_data = (lib.
                              list_and_dictionary.
                              list_to_dict(ensemble_data_tmp))

        # remove the temporary list of ensemble_data
        del ensemble_data_tmp
        
        # fix the accumulations
        self.ensemble_data = (lib.
                              fix_accumulations.
                              fix_accumulations(self.st, self.ensemble_data))

        # Check the models consistency, if they were properly loaded
        for m in self.ensemble_data.keys():
            for r in self.ensemble_data[m].keys():

                # write a log of the models,
                # runs and dates that will participate of the ensemble
                log = open(self.st["ensemble_log_directory"][0] +
                           "Effective_Dates_%s_%s.log" %
                           (m, r.strftime("%Y%m%d%H")), 'w')

                dates = list(self.ensemble_data[m][r].keys())
                dates.remove('latlon')
                dates.sort()

                for d in dates:
                    log.write("run: %s --- Data: %s \n" %
                              (r.strftime("%Y%m%d%H"), d.strftime("%Y%m%d%H")))

                log.close()
