#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/27 15:28
# FileName:

from .datasetM import Dataset


class DatasetProcessor:

    def __init__(self, sets):
        self.datasets: dict = {set_name: Dataset(set_name) for set_name in sets}

        self.__inflate()

    def __inflate(self):
        pass
