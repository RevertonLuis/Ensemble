import os
import sys
import datetime

dir_root = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + '/../') + '/'
sys.path.insert(0, dir_root)

try:
    import lib.load_settings
    import lib.target_grid
    import lib.models
    import lib.matrices_interpolation
    import lib.build_ensemble
    import lib.build_ensemble_in_parallel
    import lib.interpolated_data
    #import lib.build_xls_logs
except ImportError:
     print("")
     print("Warning: sothing wrong with the project library, can't proceed")
     print("")
     sys.exit()


# --------------------------------------------------------
if __name__ == '__main__':

    # Loading the project settings
    st = lib.load_settings.load_settings(
        dir_root + "metadata/settings.txt")

    # checking the args
    if "-date" in sys.argv:

        try:

            run = datetime.datetime.strptime(
                sys.argv[sys.argv.index("-date") + 1], "%Y%m%d%H")

            st["run"] = [run]

        except ValueError:
            print("")
            print("Date not in the format YYYYMMDDHH")
            print("Example: python main.py -date 2016020900 " +
                  "day 09, mmonth 10, year 2016 and hour 00")
            print("")
            sys.exit()

    else:

            print("")
            print("Date not in the format YYYYMMDDHH")
            print("Example: python main.py -date 2016020900 " +
                  "day 09, mmonth 10, year 2016 and hour 00")
            print("")
            sys.exit()

    if "-outfile" in sys.argv:

        try:
            st["ensemble_file"] = [sys.argv[sys.argv.index("-outfile") + 1]]
        except ValueError:
            print("")
            print("Outfile name not provided")
            print("Example: python main.py -date 2016020900 -outfile test.txt")
            print("")
            exit()

    # Cleaning old logs
    old_logs = os.listdir(st["ensemble_log_directory"][0])
    for log in old_logs:
        os.remove(st["ensemble_log_directory"][0] + log)

    # Load the target grid
    target_grid = lib.target_grid.TargetGrid(st)
    target_grid.load_target_grid()

    # Total time for the benchmarks
    t1_total = datetime.datetime.now()

    # Models
    t1 = datetime.datetime.now()
    models = lib.models.Models(st)
    models.create_ensemble_dates()
    models.check_files_availability()
    models.load_models()
    t2 = datetime.datetime.now()
    print("Time spent reading the models:", t2 - t1)
   

    # Loading the interpolated data (if it exists)
    # This must be done before models.load_models()
    # to avoid load too much unnecessary data
    t1 = datetime.datetime.now()
    hi = lib.interpolated_data.HandleInterpolations(st, models, target_grid)
    hi.load_interpolated_data()
    t2 = datetime.datetime.now()
    print("Time spent reading interpolated data:", t2 - t1)

    # Interpolate models matrices
    t1 = datetime.datetime.now()
    models.ensemble_data = (
        lib.matrices_interpolation.matrices_interpolation
        (st, models.ensemble_data, target_grid.lat, target_grid.lon, hi))
    t2 = datetime.datetime.now()
    print("Time spent interpolating the matrices", t2 - t1)

    # Save the interpolated data in a netCDF file
    # This step is convenient for many other applications
    # OBS: move the processes from interpola_matrizes to the 
    # class HandleInterpolations
    t1 = datetime.datetime.now()
    hi = lib.interpolated_data.HandleInterpolations(st, models, target_grid)
    hi.save_interpolated_data()
    t2 = datetime.datetime.now()
    print("Time spent saving the interpolated file", t2- t1)

