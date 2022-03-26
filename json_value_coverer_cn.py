# -*- coding: utf-8-*-
import os
import time
import json
from collections import OrderedDict


def show_usage():
    print('''
    =============== Usage ===============
     输入[源文件.json]与[目标文件.json]。
     如果在两个json文件中存在相同的键名；
     会读取[源文件.json]中键名对应的键值，
     并覆盖[目标文件.json]中该键名的键值。
     更新汉化版本时很有用的小工具捏~
    =====================================
    ''')


def input_json_name(tips: str):
    while True:
        file_path = input(f'\n请输入 {tips} 的路径: ')
        if os.path.isfile(file_path) and file_path[-5:] == '.json':
            break
        else:
            print('\n### 出BUG啰 ### \n#- 你这输入的是json文件吗，我咋找不到捏，检查下文件路径再试试看呗。 -#')
    return file_path


def read_json(json_file_name: str):
    with open(json_file_name, 'r', encoding='UTF-8') as file:
        output_dict = OrderedDict()
        output_dict = json.load(file)
        return output_dict


def update_json(source_json: dict, target_json: dict) -> tuple[dict, int]:
    cover_count: int = 0
    # cover value from source.json -> target.json.
    for source_key in source_json:
        if source_key in target_json:
            target_json.update({f'{source_key}': source_json[source_key]})
            cover_count = cover_count + 1
    return target_dict, cover_count


def output_file(json_dict: dict):
    file_name: str = input('\n请输入 [输出用的文件名]: ') + '.json'
    try:
        with open(file_name, 'w', encoding='UTF-8') as file:
            file.write(json.dumps(json_dict, indent=4, ensure_ascii=False))
        print(f'\n### 成功啰 ### \n#- 爷替换了足足 {cover_count} 条键值诶！ -#')
    except:
        print(f'### 出BUG啰 ### \n#- 没办法创建输出文件，你再好好检查一下吧！ -#')


if __name__ == '__main__':
    show_usage()
    source_file, target_file = input_json_name('[源文件.json]'), input_json_name('[目标文件.json]')
    source_dict, target_dict = read_json(source_file), read_json(target_file)
    new_json, cover_count = update_json(source_dict, target_dict)
    output_file(new_json)
    time.sleep(3)
