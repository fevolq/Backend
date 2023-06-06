#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2022/10/27 16:54
# FileName:

import exceptions
from dao import poolDB, db
import config


class Redis:

    def __init__(self, db_name, db_conf, use_pool) -> None:
        if use_pool:
            self.__conn = poolDB.get_coon(mode='redis', db_name=db_name, db_conf=db_conf)
        else:
            self.__conn = db.Db('redis', db_name, db_conf)

    @property
    def coon(self):
        return self.__conn

    def execute(self, action, *args, **kwargs) -> dict:
        raise_error = kwargs.pop('raise_error') if 'raise_error' in kwargs else True  # 是否扔出异常

        res = {'result': None, 'success': True}
        with self.__conn as coon:
            try:
                result = getattr(coon, action)(*args, **kwargs)
                res['result'] = result
            except Exception as e:
                res['result'] = e
                res['success'] = False
                if raise_error:
                    raise exceptions.DbException(e)

        return res


def redis_obj(
    db_name: int = None, db_conf: dict = None,
    use_pool: bool = True,
):
    if db_name is None:
        db_name = 0
    else:
        db_name = config.REDIS_DB.get(db_name, db_name)
    if db_conf is None:
        db_conf = {
            'host': config.REDIS_HOST,
            'port': config.REDIS_PORT,
            'password': config.REDIS_PWD,
        }
    return Redis(db_name, db_conf, use_pool)


def execute(
    action: str, *args,
    db_name: int = None, db_conf: dict = None,
    use_pool=True, **kwargs,
):
    redis = redis_obj(db_name=db_name, db_conf=db_conf, use_pool=use_pool)
    return redis.execute(action, *args, **kwargs)


if __name__ == '__main__':
    ...

    # # string
    # result = execute('set', 'key_string', 11, db_name=14, use_pool=False)
    # result = execute('get', 'key_string', db_name=14, use_pool=False)         # 获取单个
    # result = execute('mget', ['key_string', ], db_name=14, use_pool=False)    # 获取指定的多个key

    # # hash
    # result = execute('hset', 'key_hash', 'a', 11, db_name=14, use_pool=False)      # 单个键值对
    # result = execute('hmset', 'key_hash', {'b': 22, 'c': 'cc'}, db_name=14, use_pool=False)    # 多个键值对
    # result = execute('hget', 'key_hash', 'a', db_name=14, use_pool=True)      # 获取指定键的值
    # result = execute('hgetall', 'key_hash', db_name=14, use_pool=True)        # 获取所有键值对

    # # set
    # result = execute('sadd', 'key_set', 'a', 11, 22, db_name=14, use_pool=True)
    # result = execute('smembers', 'key_set', db_name=14, use_pool=True)

    # print(type(result['result']))
    # print(result, type(result['result']))
