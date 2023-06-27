#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/6/27 15:28
# FileName: dashboard文件配置入库

import json
import os
from typing import List

from dao import sql_builder, mysqlDB
from utils import util


class Writer:

    relative_path = '../../dashboard_files'
    absolute_path = ''

    def __init__(self, name: str, joiner='/'):
        self.name = name.lower()
        root_path = self.absolute_path or os.path.join(os.path.abspath(__file__), self.relative_path)
        self.path = os.path.join(root_path, *self.name.split(joiner)) + '.json'

    def load(self):
        with open(self.path.replace('\\', '/'), 'r', encoding='utf-8') as f:
            config = json.load(f)

        return config

    def write(self, config):
        table = 'dashboard_conf'

        row = {
            'name': self.name,
            'config': json.dumps(config, indent=4, ensure_ascii=False),
            'update_at': util.asia_local_time()
        }
        sql, args = sql_builder.gen_insert_sql(table, row, update_cols=['update_at'])
        res = mysqlDB.execute(sql, args)
        print(f'{self.name} {res}')

    def main(self):
        self.write(self.load())


def generate_paths(data, prefix='', paths: List = None, joiner='/'):
    paths = paths or []
    for key, value in data.items():
        if isinstance(value, dict):
            generate_paths(value, prefix=f"{prefix}{key}{joiner}", paths=paths)
        elif isinstance(value, list):
            for item in value:
                paths.append(f"{prefix}{key}{joiner}{item}")
        else:
            paths.append(f"{prefix}{key}{joiner}{value}")

    return paths


def from_file(file):
    """
    从单文件
    :param file: 'obj/path'
    :return:
    """
    Writer(file).main()


def from_files(files):
    """
    多文件
    files = {
        'dashboard': '',
        'filter': [],
        'chart': {
            'table': [],
            'echart': [],
        },
        'dataset': []
    }
    :param files:
    :return:
    """
    file_paths = generate_paths(files)
    for file in file_paths:
        from_file(file)


if __name__ == '__main__':
    pass

    file_ = 'dashboard/fund'
    # from_file(file_)

    files_ = {
        'dashboard': 'fund',
        'filter': ['daterange'],
        'chart': {
            'table': ['fund/fund', 'fund/fund_worth'],
            'echart': [],
        },
        'dataset': ['fund', 'fund_worth']
    }
    # from_files(files_)
