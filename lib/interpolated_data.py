import os
import netCDF4
import time
import numpy
import datetime

class HandleInterpolations():

    """ Class that handles (load, interpolate or save) interpolated data """

    def __init__(self, settings, models, target_grid):

        self.settings = settings
        self.models = models
        self.target_grid = target_grid
        self.ensemble_interp_data = {}

    def save_interpolated_data(self):

        """ Method that saves the interpolated data in a netCDF file """

        file_name = (self.settings["interpolated_directory"][0] +
                     self.settings["run"][0].
                     strftime(self.settings["interpolated_file"][0]))

        if os.path.exists(file_name):
            os.remove(file_name)

        file = netCDF4.Dataset(file_name, 'w')

        # The general lat/lon dimensions/variables
        file.createDimension(self.settings["interpolated_lat_dim_name"][0],
                             self.target_grid.lat.shape[0])

        file.createDimension(self.settings["interpolated_lon_dim_name"][0],
                             self.target_grid.lon.shape[1])

        file.createVariable(self.settings["interpolated_lat_var_name"][0], 'f',
                            (self.settings["interpolated_lat_dim_name"][0],
                             self.settings["interpolated_lon_dim_name"][0]))

        file.createVariable(self.settings["interpolated_lon_var_name"][0], 'f',
                            (self.settings["interpolated_lat_dim_name"][0],
                             self.settings["interpolated_lon_dim_name"][0]))

        file.variables[self.settings["interpolated_lat_var_name"][0]][:, :] = (
            self.target_grid.lat[:, :].astype('f'))
        file.variables[self.settings["interpolated_lon_var_name"][0]][:, :] = (
            self.target_grid.lon[:, :].astype('f'))

        file.variables[self.settings["interpolated_lat_var_name"][0]].units = (
            " ".join(self.settings["interpolated_lat_var_units"]))
        file.variables[self.settings["interpolated_lon_var_name"][0]].units = (
            " ".join(self.settings["interpolated_lon_var_units"]))

        # Variables for ModelsStrLen and ModelsNumber
        models_info = []

        # Each model + run will have a
        # (times, interpolated matrix) = (dimension, variable)
         
        # ----------- code to let the models in the order of
        # self.settings["models"]
        # for model in self.settings["models"]:
        #    if model in self.models.ensemble_data.keys():
        # --------------------------------------------------
        
        # if order is not important then
        models_list = list(self.models.ensemble_data.keys())
        models_list.sort()
        for model in models_list:

            runs = list(self.models.ensemble_data[model].keys())
            runs.sort()

            for run in runs:
                dates = list(self.models.ensemble_data[model][run].keys())
                dates.sort()

                # Creating the times dimension
                times_dim_name = (
                    self.settings["interpolated_times_dim_name"][0] + "_" +
                    model + "_" + run.strftime("%Y%m%d%H"))

                file.createDimension(times_dim_name, len(dates))

                # Creating the times variable
                times_var_name = times_dim_name
                file.createVariable(times_var_name, 'd', (times_dim_name,))
                file.variables[times_var_name].units = (
                    " ".join(
                        self.settings["interpolated_times_var_units"]))

                # Creating the model + run interpolated variable
                model_run_var_name = model + "_" + run.strftime("%Y%m%d%H")
                file.createVariable(model_run_var_name, 'f',
                    (times_dim_name,
                     self.settings["interpolated_lat_dim_name"][0],
                     self.settings["interpolated_lon_dim_name"][0]))

                # Update de list of models that are available
                models_info.append(model_run_var_name)

                # Filling the times and model + run variables
                for date, index in zip(dates, range(len(dates))):
                    date_tuple = (date.year, date.month, date.day,
                                  date.hour, date.second,
                                  date.microsecond, 0, 0, 0)

                    date_timestamp = time.mktime(date_tuple)

                    file.variables[times_var_name][index] = date_timestamp
                    file.variables[model_run_var_name][index, :, :] = (
                        self.models.ensemble_data[model][run][date][:, :])

        # The ModelStrLen and Models dimension/variable
        file.createDimension("Models", len(models_info))
        file.createDimension("ModelsStrLen", len(max(models_info, key=len)))
        file.createVariable(self.settings["interpolated_models_var_name"][0],
                            'c', ("Models", "ModelsStrLen"))

        # Update the models array
        for model, index in zip(models_info, range(len(models_info))):
            file.variables[self.settings["interpolated_models_var_name"][0]][index, :len(model)] = model[:]

            try:
                # Atributos globais para serem lidos no thredds
                setattr(file, 'GRIDTYPE', self.target_grid.GRIDTYPE)
                setattr(file, 'MAP_PROJ', self.target_grid.MAP_PROJ)
                setattr(file, 'CEN_LON', self.target_grid.CEN_LON)
                setattr(file, 'MAP_PROJ_CHAR', self.target_grid.MAP_PROJ_CHAR)
                setattr(file, 'STAND_LON', self.target_grid.STAND_LON)
                setattr(file, 'TRUELAT1', self.target_grid.TRUELAT1)
                setattr(file, 'TRUELAT2', self.target_grid.TRUELAT2)
                setattr(file, 'CEN_LAT', self.target_grid.CEN_LAT)
                setattr(file, 'DX', self.target_grid.DX)
                setattr(file, 'DY', self.target_grid.DY)
                setattr(file, 'MOAD_CEN_LAT', self.target_grid.MOAD_CEN_LAT)

            except:
                pass

        file.close()

    def load_interpolated_data(self):
        
        """ Method that reads the interpolated data from a netCDF file """
        
        # date of the oldest interpolated file
        date_oldest = (self.settings["run"][0] - 
                       datetime.timedelta(
                       hours=int(self.settings["interpolated_oldest"][0])))

        # List of accepted interpolated files
        interpolated_files = []

        # Listing all files in the interpolated files directory
        for f in os.listdir(self.settings["interpolated_directory"][0]):
            # interpolated file date
            try:

                f_date = datetime.datetime.strptime(f, "interpolated_data_%Y%m%d%H.nc")

                # check if not oldest
                if (f_date >= date_oldest and
                    len(interpolated_files) <= int(self.settings["interpolated_files"][0])):

                    interpolated_files.append(f)

            except:
                pass

        # Creating the model (outside class) ensemble_interp_data
        # ensemble_interp_data will be replaced by ensemble_data in matrices_interpolation
        self.ensemble_interp_data = {}

        for f in interpolated_files:
            self.load_interpolated_file(f)

    def load_interpolated_file(self, f):

        # each interpolated file f will have a dictionary
        interp_data = {}

        file_name = self.settings["interpolated_directory"][0] + f

        file = netCDF4.Dataset(file_name, 'r')

        # Variables for ModelsStrLen and ModelsNumber
        self.models_info = file.variables[self.settings["interpolated_models_var_name"][0]][:, :]

        for mr in self.models_info:
           
            try:
                model_run = "".join(list(mr.astype("str")))
            except TypeError:
                model_run = "".join(list(mr.astype("str"))[:(mr.mask.shape[0] - list(mr.mask).count(True))])
            
            model = model_run[:model_run.find("_")]
            run = datetime.datetime.strptime(model_run[model_run.find("_")+1:], "%Y%m%d%H")

            if model not in interp_data.keys():
                interp_data[model] = {run: {}}
            else:
                interp_data[model].update({run: {}})

            dates = file.variables["times_%s" % model_run][:]
 
            for d, index in zip(dates, range(dates.shape[0])):
               
                date = datetime.datetime.utcfromtimestamp(d)
                interp_data[model][run][date] = file.variables[model_run][index, :, :]

        # update the main dictionary
        self.ensemble_interp_data[f] = interp_data  

        # The general lat/lon dimensions/variables
        if not hasattr(self.target_grid, 'lat'):
            self.target_grid.lat = file.variables[self.settings["interpolated_lat_var_name"][0]][:, :]
            self.target_grid.lon = file.variables[self.settings["interpolated_lon_var_name"][0]][:, :]

            try:
                
                # attributes for thredds projection
                self.target_grid.GRIDTYPE = getattr(file, "GRIDTYPE")
                self.target_grid.MAP_PROJ = getattr(file, "MAP_PROJ")
                self.target_grid.CEN_LON = getattr(file, "CEN_LON")
                self.target_grid.MAP_PROJ_CHAR = getattr(file, "MAP_PROJ_CHAR")
                self.target_grid.STAND_LON = getattr(file, "STAND_LON")
                self.target_grid.TRUELAT1 = getattr(file, "TRUELAT1")
                self.target_grid.TRUELAT2 = getattr(file, "TRUELAT2")
                self.target_grid.CEN_LAT = getattr(file, "CEN_LAT")
                self.target_grid.DX = getattr(file, "DX")
                self.target_grid.DY = getattr(file, "DY")
                self.target_grid.MOAD_CEN_LAT = getattr(file, "MOAD_CEN_LAT")
        
            except:
                pass

        file.close()

