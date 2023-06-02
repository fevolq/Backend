#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/26 15:42
# FileName:

from utils.dict_to_obj import set_obj_attr
from .filterM import Filter
from .queryM import Query


class FilterProcessor:

    def __init__(self, config):
        """

        :param config: filter_area
        """
        self._config = config

        self.filters: [Filter] = []       # 包含的过滤器
        self.expand_filters = []    # 默认扩展的过滤器
        self.filter_levels = []     # 级联

        set_obj_attr(self, self._config)
        self.__inflate()

    def __inflate(self):
        filters = []
        for filter_config in self.filters:
            filter_name = filter_config['name']
            # TODO: 权限校验
            filter_obj = Filter(filter_name, filter_config)
            filters.append(filter_obj)
        self.filters = filters

    # 获取过滤器的配置
    def get_config(self):
        result = {'filters': [], 'expand_filters': self.expand_filters, 'filter_levels': self.filter_levels}
        for one_filter in self.filters:
            data = one_filter.get_config()
            result['filters'].append(data)
        return result

    # 根据query，更改过滤器的一些配置（即根据用户的选择，来更改指定的过滤器的属性）
    def load_query(self, query: Query):
        for one_filter in self.filters:
            filter_query = query.filters_query.get(one_filter.name)
            if filter_query is None:
                continue
            one_filter.load_query(filter_query)
