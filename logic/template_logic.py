#!-*coding:utf-8 -*-
# python3.7
# CreateTime: 2023/2/7 16:47
# FileName:

import status_code


def info(request):
    data = {
        'code': status_code.StatusCode.success,
        'method': request.method,
    }
    return data
