#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/6/3 17:10
# FileName: 全局缓存

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


def do(action, **kwargs):
    name = kwargs.pop('name') if 'name' in kwargs else None
    content = kwargs.pop('content') if 'content' in kwargs else None
    cache = Cache()
    return cache.do(action, name=name, content=content, **kwargs)


def get(name):
    return do("get", name=name)


def add(name, content):
    return do("add", name=name, content=content)


def update(name, content):
    return do("update", name=name, content=content)


def delete(name):
    return do("delete", name=name)


def clear():
    return do("delete")
