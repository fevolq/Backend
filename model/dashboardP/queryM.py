#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/26 15:39
# FileName:

from utils.dict_to_obj import DictToObj


class Query:

    def __init__(self, config):
        self._config = config

        self.filters_query = {filter_data['name']: DictToObj(filter_data)
                              for filter_data in self._config['filters']}
        # self.expand_filters = []    # 展开的过滤器
        # self.exclude_filters = []   # 反向排除的过滤器

        self.__inflate()

    def __inflate(self):
        pass
