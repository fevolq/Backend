#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2022/11/4 18:15
# FileName:

import threadpool
import gevent
from gevent.pool import Pool
from gevent import monkey


THREAD_POOL_SIZE = 4
GEVENT_POOL_SIZE = 4


def execute_thread(func, args_list, pools: int = 4, force_pool: bool = False):
    """
    多线程
    :param func: 单线程的执行方法
    :param args_list: 单线程的参数组成的数组。[[(args1, args2,), {'key1': value1, 'key2': value2}], ]
    :param pools: 线程池数量
    :param force_pool: 当pools大于设定的最大限制时，是否强制使用pools
    :return:
    """
    if pools > THREAD_POOL_SIZE and not force_pool:
        pools = THREAD_POOL_SIZE
    if len(args_list) <= pools:
        pools = len(args_list)
    thread_pool = threadpool.ThreadPool(pools)
    result_list = [None] * len(args_list)

    # 构造不定参数
    def tmp_f(item):
        args = item[0] if any([isinstance(item[0], tuple), isinstance(item[0], list)]) else []
        kwargs = item[-1] if isinstance(item[-1], dict) else {}
        return func(*args, **kwargs)

    # 构造回调函数
    def callback(req, result):
        result_list[task_list.index(req)] = result

    task_list = threadpool.makeRequests(tmp_f, args_list, callback)
    [thread_pool.putRequest(task) for task in task_list]
    # task_pool.poll()
    thread_pool.wait()
    return result_list


def execute_event(func, args_list, pools=4, force_pool=False):
    """
    多协程
    :param func: 单协程的执行方法
    :param args_list: 单协程的参数组成的数组。[[(args1, args2,), {'key1': value1, 'key2': value2}], ]
    :param pools: 协程池数量
    :param force_pool: 当pools大于设定的最大限制时，是否强制使用pools
    :return:
    """
    monkey.patch_socket()       # 识别IO阻塞

    if pools > GEVENT_POOL_SIZE and not force_pool:
        pools = GEVENT_POOL_SIZE
    if len(args_list) <= pools:
        pools = len(args_list)
    gevent_pool = gevent.pool.Pool(pools)

    def tmp_f(item):
        args = item[0] if any([isinstance(item[0], tuple), isinstance(item[0], list)]) else []
        kwargs = item[-1] if isinstance(item[-1], dict) else {}
        return func(*args, **kwargs)

    task_list = [gevent_pool.spawn(tmp_f, _) for _ in args_list]
    gevent.joinall(task_list)

    result_list = [task.value for task in task_list]
    return result_list
