import datetime
import numpy

# Bibliotecas do projeto
import lib.temp_linear_interp


def fix_acc_scheme_wrf(model, st, ensemble_data, ensemble_data_new):

    ensemble_data_new[model] = {}

    for run in ensemble_data[model].keys():

        ensemble_data_new[model][run] = {'latlon': ensemble_data[model]
                                         [run]['latlon']}

        dates = list(ensemble_data[model][run].keys())
        dates.remove('latlon')
        dates.sort()
        for date in dates[::int(st["ensemble_acc"][0])]:

            # Fix the wrf accumulation scheme
            # just subtract the date from a old date
            # in accordance to ensemble_acc
            if ensemble_data[model][run][date][1] != 0:

                # Compute the date_p (previous) to
                # date so that date - date_p = ensemble_acc
                date_p = (date -
                          datetime.timedelta(hours=int(st["ensemble_acc"][0])))

                # if date_p is in dates then accumulate
                if date_p in dates:
                    matrix = (ensemble_data[model][run][date][0] -
                              ensemble_data[model][run][date_p][0])
                    matrix = numpy.where(matrix < 0., 0., matrix)
                    ensemble_data_new[model][run].update({date: matrix})

                else:
                    # will be implemented later,
                    # this case is not expected for the wrf model
                    pass


def fix_acc_scheme_gfs(model, st, ensemble_data, ensemble_data_new):

    ensemble_data_new[model] = {}

    for run in ensemble_data[model].keys():

        ensemble_data_new[model][run] = {'latlon':
                                         ensemble_data[model][run]['latlon']}

        dates = list(ensemble_data[model][run].keys())
        dates.remove('latlon')
        dates.sort()
        for date in dates[::int(st["ensemble_acc"][0])]:

            # Fix the wrf accumulation scheme
            # just subtract the date from a old date
            # in accordance to ensemble_acc
            if ensemble_data[model][run][date][1] != 0:

                # In GFS case is necessary some caution with acc = 1
                # that happens at each 6 hours. If acc = 1 then
                # date_p must not be subtracted
                if ensemble_data[model][run][date][1] == 1:
                    ensemble_data_new[model][run].update({date:
                                                          ensemble_data[model]
                                                          [run][date][0]})

                if ensemble_data[model][run][date][1] > 1:
                    # Compute the date_p (previous) to
                    # date so that date - date_p = ensemble_acc
                    date_p = (date - datetime.timedelta(
                        hours=int(st["ensemble_acc"][0])))

                    # if date_p is in dates then accumulate
                    if date_p in dates:
                        ensemble_data_new[model][run].update({date:
                                                              ensemble_data
                                                              [model][run]
                                                              [date][0] -
                                                              ensemble_data
                                                              [model][run]
                                                              [date_p][0]})

                    else:
                        # if date_p not in
                        # ensemble_data[model][run] then try
                        # linear interpolation so that
                        # date_p = date - datetime.timedelta(
                        # hours=int(st["interp_tol"][0]))
                        # be in dates. If not then this date is lost
                        date_p = (date -
                                  datetime.
                                  timedelta(
                                      hours=int(
                                          st["interp_tol"][0])))

                        if date_p in dates:

                            # here the there is the following issue:
                            # the files are accumulated in 3-6 and 6-3
                            # if it's accumulated in 3 then interpolate
                            # from 0 to 3
                            # if tt's accumulated in 6 then interpolate
                            # 3(date_p) to 6
                            # after the accumulation remove the values in
                            # the interval (0-3 or 6-3)
                            # then compute the hourly value

                            # creating the dates interval for the interpolation
                            # date_p will have null matrix for
                            # accumulation starting in 3
                            dates_x = [date_p, date]

                            # the limits of the interpolation
                            if ensemble_data[model][run][date][1] == 3:
                                values_y = [numpy.zeros(
                                    ensemble_data[model][run][date][0].shape,
                                    'f'),
                                    ensemble_data[model][run][date][0]]

                            if ensemble_data[model][run][date][1] == 6:
                                values_y = [ensemble_data[model]
                                            [run][date_p][0],
                                            ensemble_data[model]
                                            [run][date][0]]

                            # The interpolation
                            dates_int, values_int = (
                                lib.temp_linear_interp.matrix_linear_interp
                                (dates_x, values_y, int(st["interp_tol"][0])))

                            # update ensemble_data_new values
                            # starts in 1 because the subtraction of the
                            # matrices
                            for i in range(1, len(dates_int)):
                                matrix = values_int[i] - values_int[i - 1]
                                matrix = numpy.where(matrix < 0., 0., matrix)
                                ensemble_data_new[model][run].update(
                                    {dates_int[i]: matrix})


def fix_acc_scheme_gefs(model, st, ensemble_data, ensemble_data_new):

    ensemble_data_new[model] = {}

    for run in ensemble_data[model].keys():

        ensemble_data_new[model][run] = {'latlon':
                                         ensemble_data[model][run]['latlon']}

        dates = list(ensemble_data[model][run].keys())
        dates.remove('latlon')
        dates.sort()
        for date in dates[::int(st["ensemble_acc"][0])]:

            # Fix the wrf accumulation scheme
            # just subtract the date from a old date
            # in accordance to ensemble_acc
            if ensemble_data[model][run][date][1] != 0:

                # In GFES case is necessary some caution with acc = 1
                # that happens at each 6 hours. If acc = 1 then
                # date_p must not be subtracted
                if ensemble_data[model][run][date][1] == 1:
                    ensemble_data_new[model][run].update({date:
                                                          ensemble_data[model]
                                                          [run][date][0]})

                if ensemble_data[model][run][date][1] > 1:
                    # Compute the date_p (previous) to
                    # date so that date - date_p = ensemble_acc
                    date_p = date - datetime.timedelta(
                        hours=int(st["ensemble_acc"][0]))

                    # if date_p is in dates then accumulate
                    if date_p in dates:
                        ensemble_data_new[model]
                        [run].update({date:
                                      ensemble_data[model][run][date][0] -
                                      ensemble_data[model][run][date_p][0]})

                    else:

                        # ------------------ REMARK ---------------------
                        # GEFS will be ALLOWED to violate interp_tol
                        # -----------------------------------------------

                        # date_p always will be date - 6 horas
                        date_p = date - datetime.timedelta(hours=6)

                        # creating the dates interval for the interpolation
                        # date_p will have null matrix because of 6 hours
                        # accumulation. Furthermore the previos is 6 hours
                        # accumulation too so it must start in 0 (null matrix)
                        dates_x = [date_p, date]

                        # the limits of the interpolation
                        values_y = [numpy.zeros(
                            ensemble_data[model][run][date][0].shape,
                            'f'), ensemble_data[model][run][date][0]]

                        # the interpolation
                        dates_int, values_int = (
                            lib.temp_linear_interp.matrix_linear_interp
                            (dates_x, values_y, 6))

                        # update ensemble_data_new values
                        # starts in 1 because the subtraction of the matrices
                        for i in range(1, len(dates_int)):
                            matrix = values_int[i] - values_int[i - 1]
                            matrix = numpy.where(matrix < 0., 0., matrix)
                            ensemble_data_new[model][run].update({dates_int[i]: matrix})


def fix_acc_scheme_cptec_eta_bam(model, st,
                                          ensemble_data,
                                          ensemble_data_new):

    ensemble_data_new[model] = {}

    for run in ensemble_data[model].keys():

        ensemble_data_new[model][run] = {'latlon':
                                         ensemble_data[model][run]['latlon']}

        dates = list(ensemble_data[model][run].keys())
        dates.remove('latlon')
        dates.sort()
        for date in dates[::int(st["ensemble_acc"][0])]:

            # fix the accumulation of the
            # acc_scheme_cptec_eta_bam
            # fix the accumulation scheme of cptec eta and bam
            if ensemble_data[model][run][date][1] != 0:

                # date_p always will be date - hours
                date_p = (
                    date -
                    datetime.timedelta(
                        hours=int(st["scheme_CPTEC_interval_%s" % model][0])))

                # creating the dates interval for the interpolation
                # date_p will have null matrix because of 6 hours
                # accumulation. Furthermore the previos is 6 hours
                # accumulation too so it must start in 0 (null matrix)
                dates_x = [date_p, date]

                # the limits of the interpolation
                values_y = [numpy.zeros(
                    ensemble_data[model][run][date][0].shape,
                    'f'), ensemble_data[model][run][date][0]]

                # the interpolation
                dates_int, values_int = (
                    lib.temp_linear_interp.matrix_linear_interp(
                        dates_x, values_y,
                        int(st["scheme_CPTEC_interval_%s" % model][0])))

                # update ensemble_data_new values
                # starts in 1 because the subtraction of the matrices
                for i in range(1, len(dates_int)):
                    matrix = values_int[i] - values_int[i - 1]
                    matrix = numpy.where(matrix < 0., 0., matrix)
                    ensemble_data_new[model][run].update({dates_int[i]: matrix})


def fix_acc_scheme_cptec_brams(model, st,
                                        ensemble_data,
                                        ensemble_data_new):

    ensemble_data_new[model] = {}

    for run in ensemble_data[model].keys():

        ensemble_data_new[model][run] = {'latlon':
                                         ensemble_data[model][run]['latlon']}

        dates = list(ensemble_data[model][run].keys())
        dates.remove('latlon')
        dates.sort()
        for date in dates[::int(st["ensemble_acc"][0])]:

            # fix the accumulation of the
            # acc_scheme_cptec_eta_bam
            # fix the accumulation scheme of cptec eta and bam
            # Corrigindo aqui a acumlacao do acc_scheme_cptec_brams
            if ensemble_data[model][run][date][1] != 0:

                # compute date_p so that
                # date - date_p = scheme_CPTEC_interval_BRAMS
                date_p = (date -
                          datetime.timedelta(
                              hours=int(st["scheme_CPTEC_interval_%s" %
                                           model][0])))

                # if date_p is in dates then accumulate
                if date_p in dates:

                    # creating the dates interval for the interpolation
                    dates_x = [date_p, date]

                    # the limits of the interpolation
                    values_y = [ensemble_data[model][run][date_p][0],
                                ensemble_data[model][run][date][0]]

                    # The interpolation
                    dates_int, values_int = (
                        lib.temp_linear_interp.matrix_linear_interp
                        (dates_x, values_y,
                         int(st["scheme_CPTEC_interval_%s" % model][0])))

                    # update ensemble_data_new values
                    # starts in 1 because the subtraction of the matrices
                    for i in range(1, len(dates_int)):
                        matrix = values_int[i] - values_int[i - 1]
                        matrix = numpy.where(matrix < 0., 0., matrix)
                        ensemble_data_new[model][run].update({dates_int[i]: matrix})


def fix_accumulations(st, ensemble_data):

    # Este novo dicionario contera apenas as dates com acumulacoes corretas
    # This dictionary will contain only the dates with the fixed accumulations
    ensemble_data_new = {}

    for model in ensemble_data.keys():

        if st["acc_scheme_%s" % model][0] == "WRF":
            fix_acc_scheme_wrf(model, st, ensemble_data,
                                        ensemble_data_new)

        if st["acc_scheme_%s" % model][0] == "GFS":
            fix_acc_scheme_gfs(model, st, ensemble_data,
                                        ensemble_data_new)

        # GEFS accumulation scheme is the same as GFS.
        # Nonetheless it will be implemented a routine for GEFS
        # accumulation scheme that allow temperal interpolation
        # that violates the interp_tol
        if st["acc_scheme_%s" % model][0] == "GEFS":
            fix_acc_scheme_gefs(model, st, ensemble_data,
                                         ensemble_data_new)

        if st["acc_scheme_%s" % model][0] == "CPTEC":
            if model == "ETA" or model == "BAM":
                fix_acc_scheme_cptec_eta_bam(model, st, ensemble_data,
                                                      ensemble_data_new)

            if model == "BRAMS":
                fix_acc_scheme_cptec_brams(model, st, ensemble_data,
                                                    ensemble_data_new)

    del ensemble_data

    return ensemble_data_new
