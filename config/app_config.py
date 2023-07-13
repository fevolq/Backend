#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/10 10:41
# FileName:

import os

APP_HOST = '0.0.0.0'
APP_PORT = 1123

# 日志路径
APP_LOG_PATH = os.path.join(os.path.dirname(__file__), '../logs/app/log')

USE_THREAD = True

# sls日志是否插入库
INSERT_SLS = True

LOAD_PATCH = True

NOT_CHECK_TOKEN_API = ('/', '/user/register', '/user/login', '/user/temp')
