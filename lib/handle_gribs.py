import os
import sys
import datetime
import contextlib
#import StringIO
import io as StringIO
import pygrib
import numpy


@contextlib.contextmanager
def stdout_redirect(where):
    sys.stdout = where
    try:
        yield where
    finally:
        sys.stdout = sys.__stdout__


def handle_grib_scheme_gfs(var_name, file_name, run, latlon=False):

    try:

        if os.path.exists(file_name):

            file = pygrib.index(file_name, 'name')
            var = file.select(name=var_name)

            # ATENCAO: work around about validDate since
            # in the case of GFS and name="Total Precipitation"
            # var[0].validDate and forecastTime are not returning
            # the expected value

            with stdout_redirect(StringIO.StringIO()) as new_stdout:
                print(var[0])

            new_stdout.seek(0)
            pygrib_message = new_stdout.read()[:-1].split()
            acc_interval = pygrib_message[6].split("-")

            # var_fc = var_forecast
            # var_fc_previous = int(acc_interval[0])
            var_fc = int(acc_interval[1])

            # accumulation, it is important to fix the accumulation later
            accumulation = int(acc_interval[1]) - int(acc_interval[0])

            # Var data_a
            # var_date_previous = run +
            # datetime.timedelta( hours = var_fc_previous )
            var_date = run + datetime.timedelta(hours=var_fc)

            # Valor da variavel
            var_value = var[0]['values']

            # Flag to load latlon from the grib
            var_latlon = None
            if latlon:
                # var_lat = var[0]["latitudes"]
                # var_lon = var[0]["longitudes"]
                var_lat, var_lon = var[0].latlons()

                # convert latlon from 0 - 360 to -180 - 180
                var_lon = numpy.where(var_lon < 180, var_lon, var_lon - 360.)

                # return var_latlon as expect by other routines
                var_latlon = (var_lat, var_lon)

            file.close()

            return var_date, var_value, var_latlon, accumulation

    except:
        return None, None, None, None


def handle_grib_scheme_cptec_eta(var_name, file_name, run, latlon=False):

    # try:

        if os.path.exists(file_name):

            file = pygrib.index(file_name, 'name')
            var = file.select(name=var_name)

            # ATENCAO: work around about validDate since
            # in the case of GFS and name="Total Precipitation"
            # var[0].validDate and forecastTime are not returning
            # the expected value

            with stdout_redirect(StringIO.StringIO()) as new_stdout:
                print(var[0])

            new_stdout.seek(0)
            pygrib_message = new_stdout.read()[:-1].split()
            acc_interval = pygrib_message[6].split("-")

            # var_fc_previous = int(acc_interval[0])
            var_fc = int(acc_interval[0])

            # accumulation, it is important to fix the accumulation later
            accumulation = int(acc_interval[0])

            # In the grib message it is showed the
            # forecast from the run beginning
            # but ETA only has 3 hours accumulation
            # and the initial value (in 0)
            if accumulation > 0:
                accumulation = 3

            # var_date_previous = run +
            # datetime.timedelta( hours = var_fc_previous )
            var_date = run + datetime.timedelta(hours=var_fc)

            # variable value
            var_value = var[0]['values']

            # Flag to load latlon from the grib
            var_latlon = None
            if latlon:
                # var_lat = var[0]["latitudes"]
                # var_lon = var[0]["longitudes"]
                var_lat, var_lon = var[0].latlons()

                # return var_latlon as expect by other routines
                var_latlon = (var_lat, var_lon)

            file.close()

            return var_date, var_value, var_latlon, accumulation

    # except:
    #    return None, None, None, None


def handle_grib_scheme_cptec_brams_bam(grib_message,
                                       file_name,
                                       run,
                                       latlon=False):

    try:

        if os.path.exists(file_name):

            file = pygrib.open(file_name)
            var = file.message(grib_message)

            with stdout_redirect(StringIO.StringIO()) as new_stdout:
                print(var)

            new_stdout.seek(0)
            pygrib_message = new_stdout.read()[:-1].split()

            acc_interval = pygrib_message[6].split("-")

            # var_fc_previous = int(acc_interval[0])
            var_fc = int(acc_interval[0])

            # accumulation, it is important to fix the accumulation later
            accumulation = int(acc_interval[0])

            # In the grib message it is showed the
            # forecast from the run beginning
            # but BRAMS and BAM only has 6 hours accumulation
            # and the initial value (in 0)
            if accumulation > 0:
                accumulation = 6

            # var_date_previous = run +
            # datetime.timedelta( hours = var_fc_previous )
            var_date = run + datetime.timedelta(hours=var_fc)

            # Valor da variavel
            var_value = var['values']

            # Flag para carregar latlon do grib
            var_latlon = None
            if latlon:
                # var_lat = var[0]["latitudes"]
                # var_lon = var[0]["longitudes"]
                var_lat, var_lon = var.latlons()

                # # convert latlon from 0 - 360 to -180 - 180
                var_lon = numpy.where(var_lon < 180, var_lon, var_lon - 360.)

                # return var_latlon as expect by other routines
                var_latlon = (var_lat, var_lon)

            file.close()

            return var_date, var_value, var_latlon, accumulation

    except:
        return None, None, None, None
