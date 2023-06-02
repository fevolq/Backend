#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/26 15:38
# FileName:

from .reader import Reader
from .queryM import Query
from .filterP import FilterProcessor
from .chartP import ChartProcessor
from .dashboardM import Dashboard


class DashboardProcessor:

    def __init__(self, name, query: dict = None):
        self.__name = name
        self.__query = Query(query) if query else None

        self.__filter_processor: FilterProcessor = None
        self.__chart_processor: ChartProcessor = None

        self.__dashboard: Dashboard = None
        self.__plugin = None

        self.__inflate()

    def __repr__(self):
        return self.__name

    @property
    def name(self):
        return self.__name

    def __inflate(self):
        self.__dashboard = Dashboard(self.name)

    # 初始化过滤器
    def __inflate_filter_p(self):
        self.__filter_processor = FilterProcessor(self.__dashboard.filter_area)

    # 初始化视图
    def __inflate_chart_p(self):
        self.__chart_processor = ChartProcessor(self.__dashboard.charts, self.__filter_processor)

    def fetch_config(self):
        """获取过滤器配置"""
        self.__inflate_filter_p()

        filter_result = self.__filter_processor.get_config()
        return filter_result

    def fetch_chart(self, chart):
        """获取chart视图数据"""
        self.__inflate_filter_p()
        self.__filter_processor.load_query(self.__query)
        self.__inflate_chart_p()

        chart_result = self.__chart_processor.get_chart(chart)
        return {
            'dashboard': self.name,
            'chart': chart_result,
        }
