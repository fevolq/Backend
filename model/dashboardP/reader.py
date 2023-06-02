#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/26 15:54
# FileName:

import json
import os


class Reader:

    root_path = r'E:\Code\Github\Backend\model\dashboard_files'

    def __init__(self, name, mod: str = 'json'):
        self.names = [name] if isinstance(name, str) else name
        self.mod = mod

    def __load_json(self):
        file_path = os.path.join(self.root_path, *self.names) + '.json'
        with open(file_path.replace('\\', '/'), 'r', encoding='utf-8') as f:
            content = json.load(f)
        return content

    def load(self):
        if self.mod == 'json':
            return self.__load_json()

    @classmethod
    def read(cls, *args, **kwargs):
        return Reader(*args, **kwargs).load()
