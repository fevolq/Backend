#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/26 15:43
# FileName:

from typing import List

import pandas as pd

from utils import pools
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

    def get_chart(self, chart_name):
        self.init_charts(chart_name)
        self._dataset_p = DatasetProcessor(set([chart.get_dataset_from_conf() for _, chart in self._charts.items()]))

        if not self._is_merge:
            chart = self._charts[chart_name]
            self.load_one_chart(chart)

            df = chart.df
            cols = {**chart.rows, **chart.cols}

            result_cols = [{
                'name': col.alias,
                'label': col.label,
                'is_dim': col.is_dim,
                'extra': col.extra,
            } for _, col in cols.items() if col.visibility.upper() == 'VISIBLE']

            data_cols = [col.alias for _, col in cols.items() if col.visibility.upper() in ('INVISIBLE', 'VISIBLE')]

            extra = chart.extra
            self.extra.update(extra)
            result_extra = self.extra
        else:
            # 聚合视图
            p_config = self._config[chart_name]
            merge_type = p_config['merge_type']
            p_cols = p_config['cols']

            pools.execute_thread(self.load_one_chart, [[(chart, )] for chart in self._charts.values()])

            cols = {}       # 所有视图使用到的col
            for chart_name, chart in self._charts.items():
                chart_cols = {**chart.rows, **chart.cols}
                cols.update({f'{chart_name}.{col_name}': col for col_name, col in chart_cols.items()})

            # 页面展示的col
            result_cols = [{
                'name': cols[col_name].alias,
                'label': cols[col_name].label,
                'is_dim': cols[col_name].is_dim,
                'extra': cols[col_name].extra,
            } for col_name in p_cols if col_name in cols and cols[col_name].visibility.upper() == 'VISIBLE']

            data_cols = [col.alias for _, col in cols.items() if
                         col.visibility.upper() in ('INVISIBLE', 'VISIBLE')]

            df = pd.DataFrame()
            last_keys = []
            for chart_name, chart in self._charts.items():
                chart_df = chart.df
                if chart_df.empty:
                    continue
                elif df.empty:
                    df = chart_df
                    last_keys = [col.alias for _, col in chart.get_dim_cols().items()]
                    continue
                keys = [col.alias for _, col in chart.get_dim_cols().items()]
                df = pd.merge(df, chart_df, how=merge_type.lower(), left_on=last_keys, right_on=keys)
                last_keys = keys        # TODO: 聚合字段待处理

            result_extra = self.extra

        df = self.reload_df(df, list(cols.values()))

        result = {
            'data': df.loc[:, data_cols].to_dict(orient='records'),
            'cols': result_cols,
            'extra': result_extra
        }
        return result

    def reload_df(self, df, cols: List[ChartCol]) -> pd.DataFrame:
        df = self.reload_cal_df(df, [col for col in cols if col.expr])
        df = self.reload_fmt_df(df, [col for col in cols if col.fmt])
        return df

    @staticmethod
    def reload_cal_df(df, cols) -> pd.DataFrame:
        # 对某些字段的值进行计算重载
        return df

    @staticmethod
    def reload_fmt_df(df: pd.DataFrame, cols: List[ChartCol]) -> pd.DataFrame:
        # 对某些字段的值进行格式化重载

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
