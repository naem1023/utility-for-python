import json
from pandas import DataFrame
import sys

json_data = None

#get file name
file_path = sys.argv[1]

#check a number of argv
if len(sys.argv) != 2:
    print("insufficient argv")

# open json file
with open(file_path) as json_file:
    json_data = json.load(json_file)

    # get array of document
    document_array = json_data["document"]

    # print(type(document_array))
    # print(document_array)
    # get array of utterance
    utterance_array = document_array[0]["utterance"]

    # get all sentence
    formList = list()
    original_formList = list()
    noteList = list()

    for item in utterance_array:
        formList.append(item["form"])
        original_formList.append(item["original_form"])
        noteList.append(item["note"])

    excelDataFrame = DataFrame({"form": formList[:], "original_form": original_formList[:], "note":noteList[:]})

    # make excel file
    excelDataFrame.to_excel("jsonToExcel.xlsx")
    
