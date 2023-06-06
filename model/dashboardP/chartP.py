#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/26 15:43
# FileName:

from .chartM import Chart
from .datasetP import DatasetProcessor
from .filterP import FilterProcessor


class ChartProcessor:

    def __init__(self, config, filter_p: FilterProcessor):
        self._config = config
        self.filter_p: FilterProcessor = filter_p
        self._dataset_p: DatasetProcessor = None

        self._charts = {}
        self.extra = {}

        self.__inflate()

    def __inflate(self):
        pass

    def init_charts(self, chart_name):
        """根据指定的chart名称，来初始化指定的chart"""
        p_config = self._config[chart_name]
        self.extra = p_config.get('extra', {})
        if not p_config:
            assert f'error chart name: {chart_name}'

        if p_config.get('merge_charts'):
            # TODO: 多视图合并。可能存在递归
            pass
        else:
            chart = Chart(p_config['path'])
            chart.chart_name = chart_name
            self._charts[chart_name] = chart
        # for chart_name, p_config in self._config.items():
        #     if not p_config.get('path'):
        #         # 聚合视图
        #         continue
        #
        #     chart = Chart(p_config['path'])
        #     self._charts[chart_name] = chart

    def load_one_chart(self, chart: Chart):
        chart.get_chart(self.filter_p, self._dataset_p)

    def get_chart(self, chart_name):
        self.init_charts(chart_name)
        self._dataset_p = DatasetProcessor(set([chart.get_dataset_from_conf() for _, chart in self._charts.items()]))
        result = {
            'data': [],
            'cols': [],
            'extra': self.extra
        }
        if self._charts.get(chart_name, None):
            chart = self._charts[chart_name]
            self.load_one_chart(chart)

            df = chart.df
            cols = {**chart.rows, **chart.cols}

            result['cols'] = [{
                'name': col.alias,
                'label': col.label,
                'is_dim': col.is_dim,
                'extra': col.extra,
            } for _, col in cols.items() if col.visibility.upper() == 'VISIBLE']

            data_cols = [col.field.alias for _, col in cols.items() if col.visibility.upper() in ('INVISIBLE', 'VISIBLE')]
            df = df.loc[:, data_cols]
            result['data'] = df.to_dict(orient='records')

            extra = chart.extra
            self.extra.update(extra)
            result['extra'] = self.extra

        else:
            p_config = self._config[chart_name]
            # TODO：聚合视图
            pass

        return result
