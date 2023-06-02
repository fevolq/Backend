#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/24 17:23
# FileName:

import status_code
from model.dashboardP import DashboardProcessor


def dashboard_config(query: dict):
    dashboard_name = query.pop('name')
    data = {
        'code': status_code.StatusCode.success,
        'data': DashboardProcessor(dashboard_name, query).fetch_config()
    }
    return data


def chart(query: dict):
    dashboard_name = query.pop('name')
    chart_name = query.pop('chart')
    data = {
        'code': status_code.StatusCode.success,
        'data': DashboardProcessor(dashboard_name, query).fetch_chart(chart_name)
    }
    return data
