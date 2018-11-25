#!/bin/bash

#-----------------------------------------------------#
#                                                     #
#	Script that runs the ensemble                 #
#                                                     #
#                                                     #
#	Reverton                                      #
#	Data: 03/04/2018                              #
#                                                     #
#-----------------------------------------------------#

source /wrf/home/.bashrc

# Find the proper date
day="$(date +%d)"
month="$(date +%m)"
year="$(date +%Y)"
hour=$(date +%H)

if [ $hour -lt 17 ]
then
   hour="00"
else
   hour="12"
fi

# Run the first part of the script.
# 1) Read the models
# 2) Interpolated the models
# 3) Save the interpolated file
python3 /dados/produtos/gera_ensemble_v2/bin/load_interpolate_save.py "-date" "$year$month$day$hour" > "/dados/produtos/gera_ensemble_v2/logs2/benchmark_$day$month$year$hour.txt" 2> "/dados/produtos/gera_ensemble_v2/logs2/errors_$day$month$year$hour.txt"

# Run the second part of the script.
# 1) Read the interpolated file from the first part (above)
# 2) Compute the ensemble
# 3) Save the ensemble file
python3 /dados/produtos/gera_ensemble_v2/bin/load_compute_save.py "-date" "$year$month$day$hour" >> "/dados/produtos/gera_ensemble_v2/logs2/benchmark_$day$month$year$hour.txt" 2>> "/dados/produtos/gera_ensemble_v2/logs2/errors_$day$month$year$hour.txt"

# Remove interpolated files older than 3 days
day2="$(date --date="3 days ago" +%d)"
month2="$(date --date="3 days ago" +%m)"
year2="$(date --date="3 days ago" +%Y)"
python3 /dados/produtos/gera_ensemble_v2/bin/remove_old_files.py  "-directory" "/dados/produtos/gera_ensemble_v2/tmp/" "-date" "$year2$month2$day2"_"$hour" "-file_date_pattern"  "interpolated_data_%Y%m%d%H.nc"

# Remove ensemble files older than 15 days
day3="$(date --date="15 days ago" +%d)"
month3="$(date --date="15 days ago" +%m)"
year3="$(date --date="15 days ago" +%Y)"
python3 /dados/produtos/gera_ensemble_v2/bin/remove_old_files.py  "-directory" "/dados/produtos/gera_ensemble_v2/tmp/" "-date" "$year3$month3$day3"_"$hour" "-file_date_pattern"  "ensemble_%Y%m%d%H.nc"

# Inserting data into the database
if [ $hour -lt 17 ]
then
/dados/produtos/ensemble_database/bin/ensemble_database.sh
fi
