import sys
import os
import netCDF4


class TargetGrid():

    def __init__(self, settings):

        self.st = settings

    def load_target_grid(self):

        """ Method that load the target grid """

        # load the target grid name (expected to be in the settings.txt file)
        self.grid_name = (self.st['directory_metadata'][0] +
                          self.st["target_grid"][0])

        if os.path.exists(self.grid_name):

            # open the metadata file
            self.file = netCDF4.Dataset(self.grid_name)

            # laod lat/lon
            self.lat = self.file.variables["latitude"][:, :]
            self.lon = self.file.variables["longitude"][:, :]

            try:

                # Atributos globais para serem lidos no thredds
                self.GRIDTYPE = getattr(self.file, "GRIDTYPE")
                self.MAP_PROJ = getattr(self.file, "MAP_PROJ")
                self.CEN_LON = getattr(self.file, "CEN_LON")
                self.MAP_PROJ_CHAR = getattr(self.file, "MAP_PROJ_CHAR")
                self.STAND_LON = getattr(self.file, "STAND_LON")
                self.TRUELAT1 = getattr(self.file, "TRUELAT1")
                self.TRUELAT2 = getattr(self.file, "TRUELAT2")
                self.CEN_LAT = getattr(self.file, "CEN_LAT")
                self.DX = getattr(self.file, "DX")
                self.DY = getattr(self.file, "DY")
                self.MOAD_CEN_LAT = getattr(self.file, "MOAD_CEN_LAT")

            except ValueError:
                pass

            # Close the file
            self.file.close()

        else:

            l1 = "WARNING"
            l2 = "Target Grid: %s not found" % self.grid_name
            l3 = "Can't proceed"
            l4 = "Shutting down the program"
            print("")
            print(int(max([len(l1), len(l2), len(l3), len(l4)]) / 2 -
                      len(l1) / 2) * " " + l1)
            print(l2)
            print(l3)
            print(l4)
            print("")
            sys.exit()
