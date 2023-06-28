#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/6/3 17:10
# FileName: 全局缓存

import re
import threading


class CacheItem:
    """
    单个缓存
    """
    def __init__(self, name, content):
        self.__name = name
        self.__content = content

    @property
    def name(self):
        return self.__name

    @property
    def content(self):
        return self.__content


class Cache:
    """
    全局缓存
    """

    __caches = {}
    __lock = threading.RLock()

    def __new__(cls, *args, **kwargs):
        # 构造单例
        if hasattr(cls, 'instance'):
            return cls.instance

        # 线程锁
        with cls.__lock:
            if not hasattr(cls, 'instance'):
                cls.instance = super(Cache, cls).__new__(cls)
            return cls.instance

    def __init__(self):
        pass

    def do(self, action, name=None, content=None, **kwargs):
        action = action.lower()
        if action == 'get':
            return self.__get(name)
        elif action == 'add':
            return self.__add(name, content)
        elif action == 'update':
            return self.__update(name, content)
        elif action == 'delete':
            return self.__delete(name)
        elif action == 'clear':
            return self.__clear()
        elif action == 'get_fuzzy':
            return self.__get_fuzzy(name)
        else:
            raise Exception(f"暂无{action}的实现")

    def __get(self, name):
        cache_item = self.__caches.get(name, None)
        return cache_item.content if cache_item else None

    def __add(self, name, content) -> bool:
        if name in self.__caches:
            raise Exception(f'已存在 cache: {name}')
        self.__caches[name] = CacheItem(name, content)
        return True

    def __update(self, name, content):
        self.__caches[name].content = content

    def __delete(self, name):
        if name in self.__caches:
            self.__caches.pop(name)

    def __clear(self):
        self.__caches.clear()

    def __get_fuzzy(self, name) -> dict:
        """
        模糊查询，类似sql中的LIKE操作
        :param name:
        :return:
        """
        pattern = name.replace('%', '.*')
        result = {key: self.__caches[key] for key in self.__caches if re.fullmatch(pattern, key)}
        return result


def do(action, **kwargs):
    name = kwargs.pop('name') if 'name' in kwargs else None
    content = kwargs.pop('content') if 'content' in kwargs else None
    cache = Cache()
    return cache.do(action, name=name, content=content, **kwargs)


def get(name):
    """
    查询，不存在则为None
    :param name:
    :return:
    """
    return do("get", name=name)


def get_fuzzy(name):
    """
    模糊查询，类似sql语句中的LIKE
    :param name:
    :return:
    """
    return do("get_fuzzy", name=name)


def add(name, content):
    """
    添加缓存
    :param name: 缓存名称
    :param content: 内容
    :return:
    """
    return do("add", name=name, content=content)


def update(name, content):
    """
    更新缓存
    :param name:
    :param content:
    :return:
    """
    return do("update", name=name, content=content)


def delete(name):
    """
    删除指定缓存
    :param name:
    :return:
    """
    return do("delete", name=name)


def clear():
    """
    清除所有缓存
    :return:
    """
    return do("clear")
