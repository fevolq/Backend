#!-*coding:utf-8 -*-
# python3.7
# CreateTime: 2023/2/22 10:55
# FileName:

import random
import time

from werkzeug.wrappers import Request

from utils import log_sls, util


class Middleware:

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        _request = Request(environ)

        now = time.time()
        environ['metadata.start_time'] = now
        environ['metadata.require_id'] = str(int(now*1000)) + ''.join([str(random.randint(1, 10)) for _ in range(6)])

        log_sls.info(
            'Middleware', '接收请求',
            start_time=util.time2str(now),
            base_url=_request.base_url,
            uri=_request.path,
            method=_request.method,
            user_agent=_request.user_agent,
            ip=_request.headers.get('X-Forwarded-For', _request.remote_addr),
            args=load_request_args(_request),
        )

        return self.app(environ, start_response)


def load_request_args(request):
    result = {
        'param': None,
        'json': None,
    }
    if request.is_json:
        result['json'] = request.json
    param_keys = request.args.keys()
    result['param'] = {} if param_keys else result['param']
    for key in param_keys:
        result['param'].update({
            key: request.args.getlist(key)
        })

    return result
