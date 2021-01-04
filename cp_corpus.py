import pandas as pd
from openpyxl import load_workbook
import os

def convert_audio(origin_dir, origin_file_name, conversion_file_name):
    for origin, conversion in zip(origin_file_name, conversion_file_name):
        info_command = "ffmpeg -i " + '"' + origin_dir + "/" + origin + '"'\
                        + " 2>&1| grep -A1 Duration"
        # result = subprocess.run([info_command], stdout=subprocess.PIPE)
        # print(result.stdout)
        
        audio_name_without_extension = conversion[:-4]
        '''
        any audio format to wav file, pcm16bit, 1 channel, 16000 sample rate.
        slice 0 second to 60 second
        '''
        print()
        convert_command = "ffmpeg -i " + '"' + origin_dir + "/" + conversion + '" '\
                            + "-acodec pcm_s16le -ar 16000 " \
                            + "-ac 1 " \
                            + '"' + origin_dir + "/" + audio_name_without_extension + ".wav" + '"'
        print()
        print(convert_command)
        os.system(convert_command)
        print()

        rm_commnd = "rm " + '"' + origin_dir + "/" + conversion + '"'
        os.system(rm_commnd)
        print(rm_commnd)

def get_file_name(xlsx_ws, num):
    origin_file_name = []
    conversion_file_name = []

    for idx, column in enumerate(xlsx_ws.columns):
        if idx == 2:
            for idx_cell, cell in enumerate(column):
                if idx_cell >= num:
                    break
                elif cell.value is None:
                    continue
                elif isinstance(cell.value, list):
                    continue
                elif cell.value == "file name":
                    continue
                origin_file_name.append(cell.value)
        elif idx == 13:
            for idx_cell, cell in enumerate(column):
                if idx_cell >= num:
                    break
                elif cell.value is None:
                    continue
                elif isinstance(cell.value, list):
                    continue
                elif cell.value == "unique no.":
                    continue
                conversion_file_name.append(cell.value)
    
    # origin_file_name = origin_file_name[6:]
    # conversion_file_name = conversion_file_name[6:]

    # print(origin_file_name)
    # print(conversion_file_name)

    return origin_file_name, conversion_file_name

def convert(origin_file_name, conversion_file_name, path):
    os.system("mkdir " + path + "/origin")
    

    for origin, conversion in zip(origin_file_name, conversion_file_name):
        mv_command = "mv " + '"' + path + "/" + origin + '" "' + path + "/origin/" + origin + '"'
        print(mv_command)
        os.system(mv_command)    

        cp_command = "cp " + '"' + path + "/origin/" + origin + '" "' + path + "/" + conversion + '"'
        print(cp_command)
        os.system(cp_command)    

    origin_path = os.path.join(path, "origin")
    target_path = os.path.join(path)
    
    convert_audio(target_path, origin_file_name, conversion_file_name)
    
        
if __name__ == "__main__":
    load_wb = load_workbook("data.xlsx", data_only=True)
    
    nu_pa = load_wb['나사렛대PA']
    nu_pm = load_wb['나사렛대PM']
    nu_nc = load_wb['나사렛대NC']

    path = 'audio/nu/pa-nu'
    origin_file_name, conversion_file_name = get_file_name(nu_pa, 50)
    convert(origin_file_name, conversion_file_name, path)

    path = 'audio/nu/pm-nu'
    origin_file_name, conversion_file_name = get_file_name(nu_pm, 56)
    convert(origin_file_name, conversion_file_name, path)

    # rm -rf audio/nu/pa-nu/*
    # cp -r /data/corpus/voice-data/working/nu/voice-files/pa-nu/* audio/nu/pa-nu
    # rm -rf audio/nu/pm-nu/*
    # cp -r /data/corpus/voice-data/working/nu/voice-files/pm-nu/* audio/nu/pm-nu