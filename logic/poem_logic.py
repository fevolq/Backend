#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/22 11:07
# FileName:
import json

import status_code
from dao import mysqlDB


def poem(query):
    res = {
        'code': status_code.StatusCode.success,
    }

    table = 'poem'
    cols = ['author', 'dynasty', 'title', 'content', 'id']
    sql = f'SELECT {", ".join(cols)} FROM {table} [WHERE] ORDER BY rand() LIMIT 1'
    args = []
    where_str = ''
    if query.get('id', None):
        where_str = 'WHERE id <> %s'
        args.append(query['id'])
    sql = sql.replace('[WHERE]', where_str)
    resp = mysqlDB.execute(sql, args)

    if not resp['success']:
        res['code'] = status_code.StatusCode.failure,
        res['msg'] = '失败'
    else:
        result = resp['result'][0]
        result['content'] = json.loads(result['content'])
        res['data'] = result

    return res


def witticism(query):
    res = {
        'code': status_code.StatusCode.success,
    }

    table = 'witticism'
    cols = ['content', 'id']
    sql = f'SELECT {", ".join(cols)} FROM {table} [WHERE] ORDER BY rand() LIMIT 1'
    args = []
    where_str = ''
    if query.get('id', None):
        where_str = 'WHERE id <> %s'
        args.append(query['id'])
    sql = sql.replace('[WHERE]', where_str)
    resp = mysqlDB.execute(sql, args)

    if not resp['success']:
        res['code'] = status_code.StatusCode.failure,
        res['msg'] = '失败'
    else:
        res['data'] = resp['result'][0]

    return res
