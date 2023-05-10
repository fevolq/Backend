#!-*- coding: utf-8 -*-
# python3.7
# CreateTime: 2023/3/11 20:20
# FileName:

import hashlib
import json
import time
import uuid
from functools import wraps

import bcrypt
from flask import request

from dao import redisDB
from model.user import User
from status_code import StatusCode

CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.!?[]%#@&*"
SALT_LENGTH = 16
SECRET_KEY = 'permission'


def gen_uid():
    return str(uuid.uuid4())


def gen_salt() -> str:
    # """生成随机固定字符串"""
    # if SALT_LENGTH <= 0:
    #     raise ValueError("Salt length must be positive")
    #
    # return "".join(secrets.choice(CHARS) for _ in range(SALT_LENGTH))
    return bcrypt.gensalt(rounds=SALT_LENGTH).decode()


def bcrypt_pwd(password) -> str:
    """
    对明文密码初次加密
    :param password: 明文密码
    :return:
    """
    result = hashlib.sha1(str(SECRET_KEY + password).encode("utf8")).hexdigest()
    return result


def gen_bcrypt_str(password, salt) -> str:
    result = bcrypt_pwd(password)
    bcrypt_str = bcrypt.hashpw(result.encode(), salt.encode()).decode()
    return bcrypt_str


def check_pwd(password, salt_record, bcrypt_str_record):
    bcrypt_str = gen_bcrypt_str(password, salt_record)
    return bcrypt_str == bcrypt_str_record


def gen_token(s) -> str:
    # token = "".join(secrets.choice(CHARS) for _ in range(32))
    token = hashlib.md5(f'{s}{time.time()}'.encode('utf-8')).hexdigest()
    return token


def insert_token(token, user_info, is_update=False):
    key = f'user:token:{token}'
    redisDB.execute('set', key, json.dumps(user_info), ex=60*60*24*7, nx=is_update)


def get_user_by_token(token):
    """
    token为空，则不查询用户；
    token存在，若失效，则uid=None；若存在，则为正常情况
    """
    if token is None:
        return User()

    key = f'user:token:{token}'
    res = redisDB.execute('get', key)['result']
    if not res:
        uid = None
    else:
        user_info = json.loads(res)
        insert_token(token, user_info, is_update=True)      # 更新过期时间
        uid = user_info.get('uid')
    return User(uid=uid)


def is_login(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        user = request.environ['metadata.user']

        if user.login:
            return {'code': StatusCode.unauthorized, 'msg': 'User not logged in'}

        return func(*args, **kwargs)

    return decorated_func


def is_admin(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        user = request.environ['metadata.user']

        if not user.is_admin():
            return {'code': StatusCode.forbidden, 'msg': 'Access Denied'}

        return func(*args, **kwargs)

    return decorated_func


def has_permission(permission):
    def do(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            user = request.environ['metadata.user']

            if not user.has_permission(permission):
                return {'code': StatusCode.forbidden, 'msg': 'Access Denied'}

            return func(*args, **kwargs)
        return decorated_func
    return do
