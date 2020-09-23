# must use python3

import pandas
from pandas import DataFrame
import sys
import kss
import numpy
import os
#get file name
file_path = sys.argv[1]

#check a number of argv
if len(sys.argv) != 2:
    print("insufficient argv")

#read xlsx file    
excel_DataFrame = pandas.read_excel(file_path)

#convert dataFrame to ndarray
excelNdArray = excel_DataFrame.to_numpy()

newExcelList = []

number = 0

# split sentence by '.'
for item in excelNdArray:
    # print("item=" + str(item))

    #if there's blank, pass
    if item[0] == 0:
        # print(number + "is NaN")
        number += 1
        continue 

    #split by '.'
    split_sentence = kss.split_sentences(item[0])
    
    # append sentence to list one by one
    for sentence in split_sentence:
        newExcelList.append(sentence)
    number+=1

# print("newExcelist")
# print(newExcelList)
# print("init len=" + str(len(newExcelList)))

# init len fo newExcelList
lenNewExcelList = len(newExcelList)

# index of newExcelList
i = 1

while lenNewExcelList != i :
    sentence = newExcelList[i]
    # print("#" + str(i) + " len=" + str(len(sentence)))

    # if last sentence of item[n] should merge with first item of item[n+1]
    
    if newExcelList[i][len(newExcelList[i])-1] != '.':
        # merge it
        newSentence = newExcelList[i] + " " + newExcelList[i+1]

        # replace list[n]
        newExcelList[i] = newSentence

        # delete list[n+1]
        newExcelList.pop(i+1)

        # minus a number of sentence
        lenNewExcelList -= 1
    i+=1

# print(newExcelList)

    
# make datagram to write new excel
newExcelDataFrame = DataFrame({"word": newExcelList[:]})

# make excel engine
# excelWriter = pandas.ExcelWriter('split_sentence.xlsx')

# make excel file with DataFrame
newExcelDataFrame.to_excel('split_sentence.xlsx', header=False, index=False)

print("convert complete!")



