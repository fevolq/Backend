#!-*coding:utf-8 -*-
# python3.7
# CreateTime: 2023/2/7 16:47
# FileName:

from status_code import StatusCode


def info(request):
    data = {
        'code': StatusCode.success,
        'method': request.method,
    }
    return data
