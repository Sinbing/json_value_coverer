#-*- coding: utf-8-*-
import os
import json
from collections import OrderedDict

def show_usage():
    print('''
    =============== Usage ===============
     Input [source.json] and [target.json]
     If a key was same in both json,
     Tool will read value in [source.json]
     and cover it in [target.json]
     Useful in localization files update.
    =====================================
    ''')


def input_json_name(tips: str):
    while True:
        file_path = input(f'\nplese input {tips} path: ')
        if os.path.isfile(file_path) is not True:
            print('\n### ERROR ### \n#- Cant find json file, retry plese. -#')
        else:
            break
    return file_path


def read_json(json_file_name: str):
    with open(json_file_name, 'r', encoding='UTF-8') as file:
        output_dict = OrderedDict()
        output_dict = json.load(file)
        return output_dict


def update_json(source_json: dict, target_json: dict):
    cover_count: int = 0
    # cover value from source.json -> target.json.
    for source_key in source_json:
        if source_key in target_json:
            target_json.update({f'{source_key}':source_json[source_key]})
            cover_count = cover_count + 1
    return target_dict, cover_count


def output_file(json_dict: dict):
    file_name: str = input('\nplese input [output file name]: ') + '.json'
    try:
        with open(file_name, 'w', encoding='UTF-8') as file:
            file.write(json.dumps(json_dict, indent=4, ensure_ascii=False))
        print(f'\n### SUCCESS ### \n#- Cover {cover_count} value done. -#')
    except:
        print(f'### ERROR ### \n#- Can\'t write output file. -#')



if __name__ == '__main__':
    show_usage()
    source_file, target_file = input_json_name('[source.json]'), input_json_name('[target.json]')
    source_dict, target_dict = read_json(source_file), read_json(target_file)
    new_json, cover_count = update_json(source_dict, target_dict)
    output_file(new_json)
    os.system('pause')
    exit(0)