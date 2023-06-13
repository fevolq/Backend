#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/26 16:36
# FileName:

import copy

import pandas as pd

from dao import mysqlDB
from model.dashboardP.util import read
from utils.dict_to_obj import set_obj_attr
from .filterP import FilterProcessor
from .filterM import Filter
from .datasetP import DatasetProcessor
from .datasetM import Dataset, Field
from .sqlG import SqlGenerator


class Chart:

    def __init__(self, file_name):
        self._config = read(('chart', file_name))
        self.chart_name = None         # 继承自 dashboard 中定义的视图名

        # ----------------------------文件配置---------------------------------
        self._title = self._config.get('title')
        self._name = self._config.get('name', file_name)
        self._dataset = self._config['dataset']
        self._rows = self._config.get('rows', [])
        self._cols = self._config.get('cols', [])
        self._sorts = self._config.get('sorts', [])
        self._conditions = self._config.get('conditions', {})
        self.limit = self._config.get('limit', 1000)
        self.extra = self._config.get('extra', {})

        # -----------------------------加载配置---------------------------------
        self.dataset: Dataset = None
        self.filters: [Filter] = None

        self.all_cols = {}        # 所有字段
        self.rows = {}            # 维度
        self.cols = {}            # 指标
        self.sorts = {}
        self.conditions = {}
        self.is_show = True

        self.execute_sql = None
        self.execute_args = None
        self.df = pd.DataFrame()

    def __repr__(self):
        return f'{self._name}[{self._title}]'

    def get_dataset_from_conf(self):
        return self._dataset

    def load(self, filter_p: FilterProcessor, dataset_p: DatasetProcessor):
        self.dataset: Dataset = dataset_p.datasets[self._dataset]
        self.filters: [Filter] = filter_p.filters

        self.__prepare()
        self.__load_filters()
        self.dataset.set_fields_alias(list(self.dataset.fields.values()), self.chart_name, self.dataset.table)

        if self.is_show:
            self.execute_sql, self.execute_args = SqlGenerator(copy.deepcopy(self)).gen()
            data = mysqlDB.execute(self.execute_sql, self.execute_args, db_name=self.dataset.db)
            self.df = pd.DataFrame(data['result'])

    def __prepare(self):
        """
        对配置进行准备处理
        :return:
        """
        self.__prepare_cols()
        self.__prepare_sorts()
        self.__prepare_conditions()

        for _, chart_col in self.all_cols.items():
            chart_col.set_field(self.dataset)

    def __prepare_cols(self):
        """初始化chart需要的字段"""
        def do(col_conf, to_=None, is_dim=False):
            to_ = {} if to_ is None else to_
            # 动态扩充字段
            step_cols, expand_args = self.__expand_col_step(col_conf)
            if len(expand_args) > 0:
                self.dataset.expand_field(mod='step', col_name=col_conf['field'], args=expand_args)

            cols = []
            for col in step_cols:
                args_cols, kwargs = self.__expand_col_args(col)
                cols.extend(args_cols)
                if kwargs:
                    self.dataset.expand_field(mod='kwargs', col_name=col['field'], kwargs=kwargs)

            for col in cols:
                chart_col = ChartCol(col)
                chart_col.is_dim = is_dim

                self.all_cols[chart_col.name] = to_[chart_col.name] = chart_col

        # 维度
        for conf in self._rows:
            do(conf, to_=self.rows, is_dim=True)

        # 指标
        for conf in self._cols:
            do(conf, to_=self.cols, is_dim=False)

        if len(self.all_cols) == 0:
            raise Exception(f"chart[{self._name}]未找到任何字段")
        elif len(self.all_cols) != len(self.rows) + len(self.cols):
            raise Exception(f"chart[{self._name}]中维度与指标有重复")

    def __prepare_sorts(self):
        for col_conf in self._sorts:
            chart_col = self.all_cols.setdefault(col_conf['field'], ChartCol(col_conf))

            chart_col.order = True if col_conf['order'] == 'desc' else False

            self.sorts[chart_col.name] = chart_col

    def __prepare_conditions(self):
        for col_name, condition in self._conditions.items():
            col: ChartCol = self.all_cols.setdefault(col_name, ChartCol({'field': col_name}))
            self.conditions[col] = condition

    def __load_filters(self):
        for one_filter in self.filters:
            relate_field = one_filter.relate_chart.get(self.chart_name, None)
            if relate_field is None:
                continue

            col: ChartCol = self.all_cols.setdefault(relate_field, ChartCol({'field': relate_field}))
            col.filter_m = one_filter
            col.is_dim = col.is_dim or one_filter.is_expand
            col.set_field(self.dataset)

            if one_filter.has_effect_value():
                self.conditions[col] = one_filter.get_condition()

    def get_dim_cols(self):
        cols: {str: ChartCol} = {col_name: col for col_name, col in self.all_cols.items() if col.is_dim}
        return cols

    @staticmethod
    def __expand_col_step(col):
        """
        范围内扩充。dataset中可定义一条规则字段即可
        {"field": "test_{expand}", "label": ["一级表头", "{expand}"], "expand": {"range":[1, 3], "step": 1}}
        =>
        {"field": "test_1", "label": ["一级表头", "1"]},
        {"field": "test_2", "label": ["一级表头", "2"]},
        :param col:
        :return: [col1, col2]、扩充参数
        """
        cols = []
        args = []
        expand = col.get('expand', None)
        if expand is None:
            return [col], args

        change_items = ['field', 'label', 'eval']
        for i in range(expand['range'][0], expand['range'][1], expand['step']):
            args.append(i)
            replace_item = '{expand}'

            new_col = copy.deepcopy(col)
            for item in change_items:
                if item not in new_col:
                    continue

                item_value = new_col[item]
                if isinstance(item_value, str):
                    item_value = item_value.replace(replace_item, str(i))
                elif isinstance(item_value, list):
                    tmp_item_value = []
                    for value in item_value:
                        value = value.replace(replace_item, str(i))
                        tmp_item_value.append(value)
                    item_value = tmp_item_value
                new_col[item] = item_value

            cols.append(new_col)
        return cols, args

    @staticmethod
    def __expand_col_args(col):
        """
        规则下标。dataset中可定义一条规则字段即可
        {"field": "test_{i}_{j}", "label": ["一级表头", "{i}~{j}"], "kwargs": [{"i": 1, "j": 5}, ]}
        => {"field": "test_1_5", "label": ["一级表头", "1~5"], "kwargs": {"i": 1, "j": 5}}
        :param col:
        :return: [col1, col2]、kwargs
        """
        cols = []
        kwargs = col.get('kwargs', None)
        if kwargs is None:
            return [col], kwargs

        change_items = ['field', 'label', 'eval']
        for args in kwargs:
            col_config = copy.deepcopy(col)
            for item in change_items:
                if item not in col_config:
                    continue

                item_value = col_config[item]
                for k, v in args.items():
                    if isinstance(item_value, str):
                        item_value = item_value.replace(f'{{{k}}}', f'{v}')
                    elif isinstance(item_value, list):
                        tmp_item_value = []
                        for value in item_value:
                            value = value.replace(f'{{{k}}}', f'{v}')
                            tmp_item_value.append(value)
                        item_value = tmp_item_value

                col_config[item] = item_value
            cols.append(col_config)
        return cols, kwargs


class ChartCol:

    def __init__(self, config):
        self._config = config

        self.__label = self._config.get('label', '')
        self.__field = self._config.get('field', '')
        self.visibility = self._config.get('visibility', 'VISIBLE')        # 是否展示。VISIBLE：查询并展示；INVISIBLE：查询并传递数据给UI，但不展示；GONE: 只查询，不传递给UI，也不展示，一般用于被依赖的列
        self.__expr = self._config.get('expr', '')
        self.__fmt = self._config.get('fmt', '')            # 值的格式化。.2f: 保留两位小数；.2%: 保留两位小数的百分比
        self.__extra = self._config.get('extra', '')

        self.field: Field = None
        self.is_dim: bool = False
        self.order: bool = None       # True: DESC, False: ASC
        self.filter_m: Filter = None

    def set_field(self, dataset: Dataset):
        if self.__field not in dataset.fields:
            if self.__field.find('.') > 0 and f'{self.__field.split(".")[0]}.*' in dataset.fields:
                dataset.expand_field(mod='*', col_name=self.__field)
            else:
                raise Exception(f'dataset[{dataset.name}] fields not found col: {self.__field}')
        self.field = dataset.fields[self.__field]

    @property
    def name(self):
        return self.__field

    @property
    def label(self):
        return self.__label or self.field.label if self.field else self.__label

    @property
    def alias(self):
        return self.field.alias if self.field else self.__field

    @property
    def extra(self):
        value = self.field.extra
        value.update(self.__extra)
        return value

    @property
    def expr(self):
        return self.__expr

    @property
    def fmt(self):
        return self.__fmt

    def __repr__(self):
        return f'{self.__field}[{self.__label}]'
