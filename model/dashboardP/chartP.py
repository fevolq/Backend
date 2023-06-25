#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/26 15:43
# FileName:

import json
import math
import re

import pandas as pd

from utils import pools, util
from .chartM import Chart, ChartCol
from .datasetP import DatasetProcessor
from .filterP import FilterProcessor


class ChartProcessor:

    def __init__(self, config, filter_p: FilterProcessor):
        self._config = config
        self.filter_p: FilterProcessor = filter_p
        self._dataset_p: DatasetProcessor = None

        self._charts: {str: Chart} = {}
        self.extra = {}
        self._is_merge = False

        self.__inflate()

    def __inflate(self):
        pass

    def init_charts(self, chart_name):
        """根据指定的chart名称，来初始化指定的chart"""
        def get_chart(file_name, name):
            chart = Chart(file_name)
            chart.chart_name = name
            return chart

        p_config = self._config[chart_name]
        self.extra = p_config.get('extra', {})
        if not p_config:
            assert f'error chart name: {chart_name}'

        if p_config.get('merge_charts'):
            self._is_merge = True
            merge_charts = p_config['merge_charts']
            for chart_name in merge_charts:
                self._charts[chart_name] = get_chart(self._config[chart_name]['path'], chart_name)
        else:
            self._charts[chart_name] = get_chart(p_config['path'], chart_name)

    def load_one_chart(self, chart: Chart):
        chart.load(self.filter_p, self._dataset_p)

    def get_all_chart_cols(self, use_chart_name: bool = True) -> {str: ChartCol}:
        """
        所有视图使用到的col
        :param use_chart_name: true：dashboard中定义的chart名; false：chart文件名
        :return: true: {chart_name.col_name: col}；false: {chart.name.col_name: col}
        """
        cols = {}
        for chart_name, chart in self._charts.items():
            name = chart_name if use_chart_name else chart.name
            cols.update({f'{name}.{col_name}': chart.all_cols[col_name] for col_name in [*chart.rows, *chart.cols]})
        return cols

    def get_expand_filter_cols(self) -> {str: ChartCol}:
        cols = {}       # filter.name: col
        filters = self.filter_p.filters
        for one_filter in filters:
            if not one_filter.is_expand:
                continue
            for chart in self._charts.values():
                if one_filter.name in chart.filter_cols and one_filter.name not in cols:
                    cols[one_filter.name] = chart.all_cols[chart.filter_cols[one_filter.name]]
        return cols

    def get_chart(self, chart_name):
        self.init_charts(chart_name)
        self._dataset_p = DatasetProcessor(set([chart.get_dataset_from_conf() for _, chart in self._charts.items()]))

        if not self._is_merge:
            chart = self._charts[chart_name]
            self.load_one_chart(chart)

            df = chart.df
            cols = self.get_all_chart_cols(True)
            expand_filter_cols = list(self.get_expand_filter_cols().values())         # 展开的过滤器的字段

            # 页面展示的col
            show_cols = [col.ui_info() for col in expand_filter_cols]
            show_cols.extend([col.ui_info() for _, col in cols.items() if col.visibility.upper() == 'VISIBLE'])

            # 数据字段
            data_cols = [col.alias for _, col in cols.items() if col.visibility.upper() in ('INVISIBLE', 'VISIBLE')]
            data_cols.extend([col.alias for col in expand_filter_cols])

            extra = chart.extra
            self.extra.update(extra)
            result_extra = self.extra
        else:
            # 聚合视图
            p_config = self._config[chart_name]
            merge_type = p_config['merge_type']
            p_cols = p_config['cols']

            if util.is_linux():
                pools.execute_thread(self.load_one_chart, [[(chart, )] for chart in self._charts.values()])
            else:
                for chart in self._charts.values():
                    self.load_one_chart(chart)

            cols = self.get_all_chart_cols(True)
            expand_filter_cols = list(self.get_expand_filter_cols().values())  # 展开的过滤器的字段

            # 页面展示的col
            show_cols = [col.ui_info() for col in expand_filter_cols]
            show_cols.extend([cols[col_name].ui_info() for col_name in p_cols
                              if col_name in cols and cols[col_name].visibility.upper() == 'VISIBLE'])

            # 数据字段
            data_cols = [col.alias for _, col in cols.items() if
                         col.visibility.upper() in ('INVISIBLE', 'VISIBLE')]
            data_cols.extend([col.alias for col in expand_filter_cols])

            df = pd.DataFrame()
            last_keys = {}
            for chart_name, chart in self._charts.items():
                chart_df = chart.df
                if chart_df.empty:
                    continue
                elif df.empty:
                    df = chart_df
                    last_keys = {filter_name: col.alias
                                 for filter_name, col in chart.get_expand_filter_cols().items()}
                    continue
                keys = {filter_name: col.alias
                        for filter_name, col in chart.get_expand_filter_cols().items()}
                intersection_keys = set(last_keys) & set(keys)      # 两个df的维度交集过滤器

                left_keys = [alias for filter_name, alias in last_keys.items() if filter_name in intersection_keys]
                right_keys = [alias for filter_name, alias in keys.items() if filter_name in intersection_keys]
                last_keys = {**keys, **last_keys}

                df = pd.merge(df, chart_df, how=merge_type.lower(), left_on=left_keys, right_on=right_keys)
            df = self.reload_df(df)

            result_extra = self.extra

        result = {
            'data': [] if df.empty else json.loads(df.loc[:, data_cols].to_json(orient='records')),
            'cols': show_cols,
            'extra': result_extra
        }
        return result

    def reload_df(self, df) -> pd.DataFrame:
        df = self.reload_cal_df(df)
        df = self.reload_fmt_df(df,)
        return df

    def reload_cal_df(self, df) -> pd.DataFrame:
        # 对某些字段的值进行计算重载
        # 存在循环依赖
        re_pattern = re.compile(r'\[(.*?)]')

        chart_cols = self.get_all_chart_cols()
        file_cols = self.get_all_chart_cols(False)

        expr_cols = [k for k, col in chart_cols.items() if col.expr]
        cal_cols = {}
        while expr_cols:
            col_name = expr_cols.pop()
            col = chart_cols[col_name]
            groups = re_pattern.findall(col.expr)

            abnormal = True
            cal_expr_cols = set()
            for group in groups:
                if group.find('.') < -1:        # 仅对依赖于其他文件字段的，才进行重载计算
                    abnormal = False
                    break
                col_ = file_cols[group]
                if col_.expr:       # 当依赖字段也有依赖时，则需先计算所依赖的字段
                    expr_cols.append(col_name)
                    abnormal = False
                    break
                else:
                    col.expr = col.expr.replace(f'[{group}]', col_.alias)
                    cal_expr_cols.add(col_.alias)
            if abnormal:
                cal_cols[col.alias] = {'expr': col.expr, 'cols': cal_expr_cols}

        def calculate_dataframe(row, values):
            for col in values['cols']:
                col_value = row.get(col, 0)
                try:
                    col_value = float(col_value)
                except:
                    col_value = 0
                exec(f'{col}={col_value}')
                if not col_value or math.isnan(col_value):
                    exec(f'{col}=0')
            try:
                result = eval(values['expr'], locals())
            except:
                result = '-'
            return result

        for col_name, v in cal_cols.items():
            df[col_name] = df.apply(lambda x: calculate_dataframe(x, v), axis=1)
        return df

    def reload_fmt_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """对某些字段的值进行格式化重载"""
        cols = [col for col in self.get_all_chart_cols().values() if col.fmt]

        def do(value, fmt):
            # if np.NaN(value):
            #     return value
            if isinstance(value, (int, float)):
                if fmt.endswith('f'):
                    fmt = f'%{fmt}'
                    value = fmt % value
                elif fmt.endswith('%'):
                    value = value * 100
                    fmt = fmt.replace('%', 'f')
                    value = f'{do(value, fmt)}%'
            return value

        for col in cols:
            col_name = col.alias
            if col_name not in df.columns:
                continue
            df[col_name] = df.apply(lambda x: do(x[col_name], col.fmt), axis=1)
        return df
