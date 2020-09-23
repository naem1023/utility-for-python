# Warning
- must use python3
- install numpy, pandas, openpyxl

## getSentenceFromJson.py
Get data of form, original_form, note from json

~~~
$ python3 getSentenceFromJson.py sample_json.json
~~~

## modify.py
* Merge, delete blank, split senetence.
* outputfile = split_senetece.xlsx
~~~
$ python3 modify.py sample.xlsx
~~~

## merge.py
* Just merge multiple csv file in target directory
* output file will be located in target directory
* outputfile = mergedCSV.csv

1. Using without parameter
    merge csv files located in current directory
~~~
python3 merge.py
~~~

2. Using with parameter
    merge csv files locatee in targt directory
~~~
python merge.py $targetDIR
~~~