import os
import sys
import datetime


def remove_old_files(directory, date_ref, file_date_pattern=None):

    """ Routine that remove files from directory older then date """

    # Listing all files in the directory
    for f in os.listdir(directory):

        # if file_date_pattern == None means
        # the date that the file was modified will be used
        # Getting the date that the file was
        # last modified
        if file_date_pattern is None:
            date_file = datetime.datetime.fromtimestamp(os.path.getmtime(directory + f))
        else:
            try:
                date_file = datetime.datetime.strptime(f, file_date_pattern)
            except ValueError:
                date_file = None

        # if date_lm < date remove the file
        if date_file is not None:
            if date_file < date_ref:
                os.remove(directory + f)

if __name__ == "__main__":

    # checking the args
    if "-directory" in sys.argv:

        try:

            directory = sys.argv[sys.argv.index("-directory") + 1]

        except ValueError:
            print("")
            print("Files directory not provided")
            print("Example: python3 remove_old_files.py "
                  "-directory /tmp/files_old/")
            print("")
            sys.exit()

    else:

        print("")
        print("Files directory not provided")
        print("Example: python3 remove_old_files.py "
              "-directory /tmp/files_old/")
        print("")
        sys.exit()

    # checking the args
    if "-date" in sys.argv:

        try:

            date = (datetime.
                    datetime.
                    strptime(sys.argv[sys.argv.index("-date") + 1],
                             "%Y%m%d_%H"))

        except ValueError:
            print("")
            print("Date reference provided not in the format %Y%m%d_%H")
            print("Example: python3 remove_old_files.py "
                  "-directory /tmp/files_old/ "
                  "-date 20181022_00")
            print("")
            sys.exit()

    else:

        print("")
        print("Date reference not provided")
        print("Example: python3 remove_old_files.py "
              "-directory /tmp/files_old/ "
              "-date 20181022_00")
        print("")
        sys.exit()

    # checking the args
    fdp = None
    if "-file_date_pattern" in sys.argv:

        try:

            fdp = sys.argv[sys.argv.index("-file_date_pattern") + 1]

        except ValueError:
            print("")
            print("File/date pattern not provided")
            print("Example: python3 remove_old_files.py "
                  "-directory /tmp/files_old/ "
                  "-date 20181022_00 "
                  "-file_date_pattern siprec_%Y%m%d_%H")
            print("")
            sys.exit()

    # main routine
    remove_old_files(directory, date, fdp)
