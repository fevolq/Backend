#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/26 16:36
# FileName:

from dao import mysqlDB
from exceptions import TipsException
from .reader import read
from utils.dict_to_obj import set_obj_attr


class Filter:

    def __init__(self, name, p_config):
        self._config = read('/'.join(('filter', p_config['path']))) if p_config.get('path') else {}
        self._config.update(p_config)

        # -------------------------------默认配置---------------------------------
        self.name = name
        self.title = None
        self.type = 'input'        # 过滤器类型。input、date、single、multiple
        self.default_value = None
        self.enable_exclude = False  # 是否可排除（反向选择）
        self.enable_expand = False   # 是否可展开
        self.required = False       # 是否必填
        self.extra = {}             # 直接透传至前端
        self.relate_chart = None        # 关联至视图的字段

        self.label_format = "{label}"
        self.options = []
        self.data_source = None

        set_obj_attr(self, self._config)

        self.__sql = None
        # -------------------------------加载配置---------------------------------
        self.__is_expand = self.enable_expand and False
        self.__is_exclude = self.enable_exclude and False
        self.__values = None

    def __repr__(self):
        return f'{self.name}[{self.title}]'

    # 根据data_source查询数据库
    def _fill_option(self):
        data_source = DataSource(self.data_source)
        self.options = data_source.options
        self.__sql = data_source.execute_sql

    def load_options(self):
        """加载可选值"""
        if not self.options:
            if not self.data_source:
                return None
            # 查询数据库
            self._fill_option()
        options = [{'label': self.label_format.format(label=item['label'], value=item['value']), 'value': item['value']}
                   for item in self.options]
        return options

    def get_config(self):
        """自身默认配置"""
        options = self.load_options()
        return {
            'name': self.name,
            'title': self.title,
            'type': self.type,
            'default_value': self.default_value,
            'enable_exclude': self.enable_exclude,
            'enable_expand': self.enable_expand,
            'options': options,
            'sql': self.__sql,
            'extra': self.extra,
            'required': self.required,
        }

    def load_query(self, filter_query):
        self.__is_expand = filter_query.get('is_expand', self.__is_expand)
        self.__is_exclude = filter_query.get('is_exclude', self.__is_exclude)
        self.__values = filter_query.get('values', self.__values)

        self._check_query()

    def _check_query(self):
        if self.required and not self.__values:
            raise TipsException(f'过滤器[{self.title}]必填')

    def has_effect_value(self):
        return self.values or self.is_exclude

    def get_condition(self) -> dict:
        op = '=' if not self.is_exclude else '!='
        if self.type == 'input':
            op = 'LIKE' if not self.is_exclude else 'NOT LIKE'
        elif self.type == 'inputs':
            op = 'LIKES' if not self.is_exclude else 'NOT LIKES'
        elif self.type == 'single':
            op = '=' if not self.is_exclude else '!='
        elif self.type == 'multiple':
            op = 'IN' if not self.is_exclude else 'NOT IN'
        elif self.type == 'range' or self.type == 'daterange':
            op = 'BETWEEN' if not self.is_exclude else 'NOT BETWEEN'

        return {op: self.values}

    @property
    def is_expand(self):
        return self.enable_expand and self.__is_expand

    @property
    def is_exclude(self):
        return self.enable_exclude and self.__is_exclude

    @property
    def values(self):
        return self.__values


class DataSource:

    def __init__(self, config):
        self._config = config

        self.sql = None
        self.table = None
        self.label_field = None
        self.value_field = None
        set_obj_attr(self, self._config)

        self.execute_sql = ''
        self.options = []

        self.__inflate()

    def __inflate(self):
        assert any([self.sql, self.table])

        from_table = f'({self.sql}) AS `table`' if self.sql else f'`{self.table}` AS `table`'
        self.execute_sql = f'SELECT `table`.`{self.label_field}` AS "label", `table`.`{self.value_field}` AS "value"' \
                           f' FROM {from_table} GROUP BY {self.value_field}'

        res = mysqlDB.execute(self.execute_sql)
        self.options = res['result']
