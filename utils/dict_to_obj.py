#!-*- coding:utf-8 -*-
# python3.7
# Create time: 2022/10/14 15:37
# Filename: 字典转换为对象

class Obj(dict):
    def __init__(self, name: str = None):
        self.__name = name if name is not None else 'obj'
        super().__init__()

    def __repr__(self):
        return self.__name

    # 实现object.attr
    def __getitem__(self, key):
        return self.__dict__.get(key, None)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)


class DictToObj:
    def __init__(self, dictionary, name: str = None):
        self.__name = name if name is not None else 'obj'
        for key in dictionary:
            setattr(self, key, dictionary[key])

    def __repr__(self):
        return self.get('name', self.__name)

    def __getitem__(self, key):
        return self.__dict__.get(key, None)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)


def dict_to_obj(data: dict, obj_name='obj'):
    obj = Obj(obj_name)
    set_obj_attr(obj, data, define=False)
    return obj


def set_obj_attr(obj: object, data: dict, define=True):
    """注：无法适配私有属性"""
    for attr, value in data.items():
        if define and not hasattr(obj, attr):
            continue
        setattr(obj, attr, value)


if __name__ == '__main__':
    d = {'a': 1, 'b': 2}
    o = dict_to_obj(d, 'test')
    print(o)
    print(o.a)
    print(o.get('b', 'bb'))
