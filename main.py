#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/10 10:40
# FileName:

import logging
import time

from flask import Flask, request, jsonify
from gevent import monkey

import config
from middleware import Middleware
from utils import log_util, util
import status_code
import controller

if config.LOAD_PATCH and util.is_linux():
    monkey.patch_all()


# 日志初始化
log_util.init_logging(config.APP_LOG_PATH, datefmt='%Y-%m-%d %H:%M:%S')


app = Flask(__name__)
# # 跨域
# from flask_cors import CORS
# CORS(
#     app,
#     resources='*',
#     origins='*',
#     methods=['GET', 'POST'],
#     expose_headers='*',
#     allow_headers='*',
#     supports_credentials=True,
# )

for url_prefix, blueprint in controller.blueprint.items():
    app.register_blueprint(blueprint, url_prefix=f'/{url_prefix}')
    logging.info(f'register blueprint: {url_prefix}')


@app.before_request
def before_call():
    ...
    # 若 return ，则直接返回响应
    return Middleware()()


@app.after_request
def after_call(response):
    ...
    response.headers['metadata.spent'] = f'{time.time() - request.environ["metadata.start_time"]} ms'
    response.headers['metadata.require_id'] = request.environ['metadata.require_id']
    return response


@app.errorhandler(Exception)
def error_handler(e):
    """
    全局异常捕获
    :param e:
    :return:
    """
    logging.error(e)
    data = {
        'code': status_code.StatusCode.failure,
        'msg': '出现未知情况',
    }
    return jsonify(data)


@app.route('/', methods=['GET'])
def hello():
    return 'HELLO WORLD!'


if __name__ == '__main__':
    app.run(
        host=config.APP_HOST,
        port=config.APP_PORT,
        debug=False,
        threaded=config.USE_THREAD,
    )
