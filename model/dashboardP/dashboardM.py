#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/26 15:56
# FileName:

from .reader import read
from utils.dict_to_obj import set_obj_attr


class Dashboard:

    def __init__(self, name):
        self._config = read('/'.join(('dashboard', name)))
        self._name = name

        self.title = None
        self.filter_area = None
        self.charts = None
        set_obj_attr(self, self._config)

    def __repr__(self):
        return f'{self._name}[{self.title}]'
