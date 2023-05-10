#!-*coding:utf-8 -*-
# python3.7
# CreateTime: 2023/2/22 10:55
# FileName:

import random
import time

import flask

from model.bean import user_util
from utils import log_sls, util


class Middleware:

    def __init__(self):
        flask.g.metadata = {}
        pass

    def __call__(self):
        """
        请求前置处理
        :return: 若返回，则直接返回响应
        """
        now = time.time()
        require_id = str(int(now*1000)) + ''.join([str(random.randint(1, 10)) for _ in range(6)])

        def update_request():
            """请求request的预制处理"""
            res = {}
            with flask.current_app.app_context():
                flask.request.environ['metadata.start_time'] = now
                flask.request.environ['metadata.require_id'] = require_id

                token = flask.request.headers.get('token')
                flask.request.environ['metadata.user'] = user = user_util.get_user_by_token(token)

                res['sls'] = {
                    'start_time': util.time2str(now),
                    'base_url': flask.request.base_url,
                    'uri': flask.request.path,
                    'method': flask.request.method,
                    'user_agent': flask.request.user_agent,
                    'ip': flask.request.headers.get('X-Forwarded-For', flask.request.remote_addr),
                    'user': user.uid,
                    'args': load_request_args(flask.request),
                }
            return res

        result = update_request()
        flask.g.metadata['require_id'] = require_id

        log_sls.info('Middleware', '接收请求', **result.get('sls', {}))


def load_request_args(request_):
    result = {
        'param': None,
        'form': None,
        'json': None,
    }

    if request_.is_json:
        result['json'] = request_.json

    if request_.args.keys():
        result['param'] = {
            key: request_.args.getlist(key)
            for key in request_.args.keys()
        }

    if request_.form.keys():
        result['form'] = {
            key: request_.form.getlist(key)
            for key in request_.form.keys()
        }

    return result
