#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/6/28 10:44
# FileName:

from status_code import StatusCode
from model.dashboardP import reader


def del_cache(query):
    name = query.get('name', None)
    if not name:
        return {'code': StatusCode.success}

    name = name.lower()
    if name == 'dashboard':
        reader.clear_cache()
    else:
        return {'code': StatusCode.is_conflict}

    return {'code': StatusCode.success}
