#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/26 15:54
# FileName:

import json
import os
from functools import wraps

from model.bean import cache
from utils import util


def with_cache(name):
    def do(func):
        @wraps(func)
        def decorate(*args, **kwargs):
            if util.is_linux() and cache.get(name):
                res = cache.get(name)
            else:
                res = func(*args, **kwargs)
                if util.is_linux():
                    cache.add(name, res)
            return res

        return decorate
    return do


class Reader:

    root_path = r'E:\Code\Github\Backend\model\dashboard_files'

    def __init__(self, name, mod: str = 'json'):
        self.names = [name] if isinstance(name, str) else name
        self.hash_name = util.md5(str(self.names))
        self.mod = mod

    def __load_json(self):
        file_path = os.path.join(self.root_path, *self.names) + '.json'
        with open(file_path.replace('\\', '/'), 'r', encoding='utf-8') as f:
            content = json.load(f)
        return content

    def load(self):
        @with_cache(self.hash_name)
        def __load():
            if self.mod == 'json':
                return self.__load_json()

        return __load()

    @classmethod
    def read(cls, *args, **kwargs):
        return Reader(*args, **kwargs).load()
