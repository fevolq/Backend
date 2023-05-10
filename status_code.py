#!-*coding:utf-8 -*-
# python3.7
# CreateTime: 2023/2/22 10:56
# FileName:


class StatusCode:
    success = 200

    # 要求身份认证
    unauthorized = 401

    # 拒绝执行请求
    forbidden = 403

    # 无法根据请求内容完成请求
    is_conflict = 406

    failure = 500
