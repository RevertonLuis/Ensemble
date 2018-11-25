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
    import lib.build_ensemble
    import lib.build_ensemble_in_parallel
    import lib.models_weights
    import lib.interpolated_data
    #import lib.build_xls_logs
except ImportError:
     print("")
     print("Warning: sothing wrong with the project library, can't proceed")
     print("")
    sys.exit()


# ---------------------------------------------------------
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

    # Load target_grid instance but not the file
    # the information about the target_grid will be loaded
    # from the interpolated file for st["run"]
    target_grid = lib.target_grid.TargetGrid(st)

    # Load models instance but not the models. The models
    # are loaded from the interpolated file for st["run"]
    models = lib.models.Models(st)
    models.create_ensemble_dates() 

    # Change st["interpolated_oldest"] = 0
    # This way only the interpolated file for the st["run"]
    # will be loaded. If there is no interpoalted for st["run"]
    # then something must be wrong with with load_interpolate_save.py
    st["interpolated_oldest"][0] = 0

    # This must be done before models.load_models()
    # to avoid load too much unnecessary data
    t1 = datetime.datetime.now()
    hi = lib.interpolated_data.HandleInterpolations(st, models, target_grid)
    hi.load_interpolated_data()
    t2 = datetime.datetime.now()
    print("Time spent reading interpolated data:", t2 - t1)

    # Load the ensemble interp_data from the hi class above
    models.ensemble_data = hi.ensemble_interp_data[list(hi.ensemble_interp_data.keys())[0]]

    # Computes the models weights matrices
    # The weights matrices will be applied to the interpolated matrices
    t1 = datetime.datetime.now()
    lib.models_weights.compute_models_weights_from_members(st)
    lib.models_weights.compute_models_weights_matrices(models, target_grid)
    t2 = datetime.datetime.now()
    print("Time spent computing/loading the weights", t2 - t1)

    # Build the ensemble
    t1 = datetime.datetime.now()
    #lib.build_ensemble.build_ensemble(st, models.ensemble_data,
    #                                  models.dates, target_grid)
    # Build the ensemble in parallel
    lib.build_ensemble_in_parallel.build_ensemble(st, models.ensemble_data,
                                                  models.dates, target_grid)

    t2 = datetime.datetime.now()
    print("Time spent building and saving the ensemble", t2 - t1)
    print("")

    # Make xls logs for the ensemble 
    #lib.build_xls_logs.main(st)
    
