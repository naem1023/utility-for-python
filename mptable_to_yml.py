import yaml
from tqdm import tqdm

file_name = "mp_ls_table.txt"
output_file_anme = "mp_ls_table.yaml"

'''
structure of buffer
[index, [token, tag], [token, tag] ....]
eg. if first characters are NWRW1800000021-0003-00001-00001_001
    last number(001) is index.
'''

def merge_word(buffer):
    word_dict = {}
    word_list = []

    # remove index number
    buffer.pop(0)

    sentence = ""
    # merge token to make sentence
    for word in buffer:
        sentence += word[0] + " "

    # remove last space(" ")
    sentence = sentence[:-1]
    # print("|",sentence,"|")

    # merge {token, tag} to a list
    for word in buffer:
        temp_dict = {}
        # write toekn
        temp_dict["token"] = word[0]
        # write tag
        temp_dict["tag"] = word[1]
        word_list.append(temp_dict)
    
    word_dict[sentence] = word_list

    return word_dict

if __name__ == "__main__":
    yaml_obejct = {}
    
    with open(file_name, 'r') as input_file:
        num_lines = sum(1 for line in input_file)
    with open(file_name, 'r', encoding='utf-8') as input_file:
        pbar = tqdm(total = num_lines + 1)

        buffer = []
        yaml_list = []
        while True:
            line = input_file.readline()
            if line == "" or line is None:
                break
            line_split = line.split("\t")
            # print(line_split)

            index = line_split[0].split("-")[3].split("_")[1]
            # if buffer is empty, append new sentence
            if len(buffer) == 0:
                buffer.append(index)
                word = [line_split[1], line_split[2]]
                buffer.append(word)
            # if index number of buffer is same, append this line
            elif index != "001":
                word = [line_split[1], line_split[2]]
                buffer.append(word)
            # if index number of buffer is diff
            # write buffer to output file, erase buffer and append new sentence
            elif index == "001":
                yaml_list.append(merge_word(buffer))
                buffer = []
                buffer.append(index)
                word = [line_split[1], line_split[2]]
                buffer.append(word)
            
            pbar.update(1)
        pbar.close()
                
        print("writing yaml file...")
        with open(output_file_anme, 'w') as output_file:
            yaml.dump(yaml_list, output_file, allow_unicode=True, sort_keys=False)
            
