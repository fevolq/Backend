#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/6/6 16:21
# FileName: 自定义异常

from status_code import StatusCode


class CustomException(Exception):

    def __init__(self):
        self.message = '出现未知情况'
        self.code = StatusCode.failure

    def __str__(self):
        return self.message


class DbException(CustomException):

    """数据库异常"""

    def __init__(self, message):
        self.message = message
        self.code = StatusCode.failure

    def __str__(self):
        return '异常'


class TipsException(CustomException):

    """提示"""

    def __init__(self, message):
        self.message = message
        self.code = StatusCode.is_conflict

    def __str__(self):
        return self.message
