import os, glob
import sys
import pandas

target_DIR = ""
# check a number of argv
# if there's no argv, set target DIR is now location
if len(sys.argv) != 2:
    target_DIR = "./"
# set target DIR
else:
    target_DIR = sys.argv[1]


# get all file name in target dir
files = os.listdir(target_DIR)

# get all file name, ends with ".csv"
all_csv_filename = [item for item in files if item.endswith('.csv')]

dataframe_list = []

# change current dir to target dir
os.chdir(target_DIR)

# get all csv to dataframe
for csv_filename in all_csv_filename:
    if csv_filename == 'mergedCSV.csv':
        continue
    # read csv without header
    # add new header
    csv_dataframe = pandas.read_csv(csv_filename, names=['sentence', 'classification'], header=None)

    dataframe_list.append(csv_dataframe)

    

merged_list = pandas.concat(dataframe_list)

merged_dataframe = pandas.DataFrame(merged_list)

merged_dataframe.to_csv("./mergedCSV.csv", header=False, index=False)




