#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/26 16:46
# FileName:

from .reader import Reader


def read(names):
    """

    :param names: (所属对象：dashboard、chart、filter, 文件名)
    :return:
    """
    config = Reader.read(names)
    prefabs = set()
    while config.get('prefab'):
        prefab = config.pop('prefab')
        if prefab in prefabs:
            raise Exception(f'{names[0]}[{names[1]}]存在相互引用: {prefab}')
        prefab_config = Reader.read([names[0], prefab])
        config.update(prefab_config)
    return config
