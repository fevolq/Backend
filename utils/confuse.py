#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/6/26 14:20
# FileName: 字段混淆

import itertools
import sys
from typing import List


class Confuse:
    """混淆"""

    def __init__(self):
        self._cache = {}
        self._hash_gen = self._gen_hash()

    @staticmethod
    def _gen_hash():
        s = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
             'v', 'w', 'x', 'y', 'z'}
        for i in range(1, sys.maxsize):
            yield from itertools.permutations(s, i)

    def _gen(self):
        return ''.join(next(self._hash_gen))

    def hash_value(self, value: str):
        result = self._cache.get(value, self._gen())
        self._cache[value] = result
        return self._cache[value]

    def hash_values(self, values: List[str]):
        return {value: self.hash_value(value) for value in values}

    def hash_dict(self, row: dict, item):
        row[item] = self.hash_value(row[item])

    def hash_rows(self, rows: List[dict], item):
        for row in rows:
            self.hash_dict(row, item)


if __name__ == '__main__':
    data = [
        {'field': 'code', 'label': '代码'},
        {'field': 'price', 'label': '价格'},
    ]
    Confuse().hash_rows(data, 'field')
    print(data)
