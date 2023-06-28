#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/26 15:54
# FileName:

import json
import os
from functools import wraps

from dao import sql_builder, mysqlDB
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


def clear_cache():
    """清除dashboard配置缓存"""
    dashboard_caches = cache.get_fuzzy('dashboard.%')
    for cache_name in dashboard_caches:
        cache.delete(cache_name)


class Reader:

    relative_path = '../../dashboard_files'
    absolute_path = ''

    def __init__(self, name: str, mod: str = 'json'):
        """

        :param name: path/file
        :param mod:
        """
        self.name = name.lower()
        self.cache_name = f'dashboard.{self.name}'
        self.mod = mod

    def __load_json(self):
        root_path = self.absolute_path or os.path.join(os.path.abspath(__file__), self.relative_path)
        file_path = os.path.join(root_path, *self.name.split('/')) + '.json'
        with open(file_path.replace('\\', '/'), 'r', encoding='utf-8') as f:
            content = json.load(f)
        return content

    def __load_db(self):
        table = 'dashboard_conf'

        sql, args = sql_builder.gen_select_sql(table, ['config'], condition={'name': {'=': self.name}}, limit=1)
        res = mysqlDB.execute(sql, args)['result']
        return json.loads(res[0]['config'])

    def load(self):
        @with_cache(self.cache_name)
        def __load():
            if self.mod == 'json':
                return self.__load_json()
            elif self.mod == 'db':
                return self.__load_db()

        return __load()

    @classmethod
    def read(cls, *args, **kwargs):
        return Reader(*args, **kwargs).load()


def read(name):
    """

    :param name: 文件路径，以/分隔
    :return:
    """
    mod = 'db' if util.is_linux() else 'json'
    config = Reader.read(name, mod=mod)

    prefabs = set()
    while config.get('prefab'):
        file_paths = name.split('/')
        prefab = config.pop('prefab')
        if prefab in prefabs:
            raise Exception(f'{name}]存在相互引用: {prefab}')
        prefab_paths = prefab.split('/')
        # 处理路径后退（如：../..）
        for prefab_path in prefab_paths:
            if prefab_path == '.':
                continue
            elif prefab_path == '..':
                file_paths.pop()
            else:
                file_paths.append(prefab_path)

        name = '/'.join(file_paths)
        prefab_config = Reader.read(name, mod=mod)
        config.update(prefab_config)

    return config
