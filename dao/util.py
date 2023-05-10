#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2022/12/2 17:18
# FileName: 数据库工具

import logging
import time
from typing import List

from dao import redisDB


def add_lock(lock_key, lock_value, db_name=None, timeout: int = 10, time_sleep: float = 0.1):
    """
    加锁
    :param lock_key: 锁的键名
    :param lock_value: 锁的值
    :param db_name:
    :param timeout: 锁的超时时间
    :param time_sleep: 等待时间
    :return:
    """
    while True:
        lock_res = redisDB.execute('set', lock_key, lock_value, nx=True, ex=timeout, db_name=db_name, raise_error=True)
        if all(list(lock_res.values())):
            logging.info(f'锁键: {lock_key}, 锁值: {lock_value} 加锁成功')
            break
        logging.info(f'锁键: {lock_key}, 锁值: {lock_value} 等待加锁')
        time.sleep(time_sleep)


def release_lock(lua_script: str = None, keys: List = None, args: List = None) -> bool:
    """
    lua事务脚本。校验锁 >> 更改值 >> 解锁
    :param lua_script: lua脚本
    :param keys: 脚本的KEYS
    :param args: 脚本的ARGV
    :return:
    """
    # KEYS = [锁的关键字, 被锁关键字]
    # ARGV = [校验锁的值， 被锁关键字的新值, 使用的数据库]
    redis_db = redisDB.redis_obj()
    with redis_db.coon as coon:
        cmd = coon.register_script(lua_script)
        cmd_res = cmd(keys=keys, args=args)
        if cmd_res:
            logging.info(f'lua脚本 success')
            logging.info(f'解锁成功')
        return cmd_res


if __name__ == '__main__':
    demo_scripts = """
    -- 切换数据库
    redis.call('SELECT', ARGV[3])
    
    -- 校验锁值
    if redis.call('GET', KEYS[1]) ~= ARGV[1] then
        return 0
    end
    
    -- 更改关键词的值
    if not redis.call('SET', KEYS[2], ARGV[2]) then
        -- redis.call('DEL', KEYS[1])      -- 若解锁失败，则可等待锁超时
        return 0
    end
    
    -- 解锁
    return redis.call('DEL', KEYS[1])
    """
    demo_keys = ['lock_key', 'word_key']
    demo_args = ['lock_value', 'word_value', 15]
    # res = release_lock(demo_scripts, demo_keys, demo_args)
    # print(res)

    # add_lock('lock_key', 'lock_value', db_name=15, timeout=100)
