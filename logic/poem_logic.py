#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/22 11:07
# FileName:
import json

import status_code
from dao import mysqlDB, sql_builder


def poem(query):
    res = {
        'code': status_code.StatusCode.success,
    }

    table = 'poem'
    cols = ['author', 'dynasty', 'title', 'content', 'id']
    sql = f'SELECT {", ".join(cols)} FROM {table} [WHERE] ORDER BY rand() LIMIT %s'
    args = []
    where_str = ''
    if query.get('id', None):
        ids = [str(item).strip() for item in str(query['id']).split(',')]
        if len(ids) == 1:
            where_str = 'WHERE `id` <> %s'
            args.extend([int(item) for item in ids])
        else:
            where_str, where_args = sql_builder.gen_wheres_part(table, {'id': {'NOT IN': ids}})
            where_str = f'WHERE {where_str}'
            args.extend([int(item) for item in where_args])

    size = query['size'] if query.get('size', None) else 1
    args.append(int(size))
    sql = sql.replace('[WHERE]', where_str)
    resp = mysqlDB.execute(sql, args)

    if not resp['success']:
        res['code'] = status_code.StatusCode.failure,
        res['msg'] = '失败'
    else:
        for result in resp['result']:
            result['content'] = json.loads(result['content'])
        res['data'] = resp['result']

    return res


def witticism(query):
    res = {
        'code': status_code.StatusCode.success,
    }

    table = 'witticism'
    cols = ['content', 'id']
    sql = f'SELECT {", ".join(cols)} FROM {table} [WHERE] ORDER BY rand() LIMIT %s'
    args = []
    where_str = ''
    if query.get('id', None):
        ids = [str(item).strip() for item in str(query['id']).split(',')]
        if len(ids) == 1:
            where_str = 'WHERE `id` <> %s'
            args.extend([int(item) for item in ids])
        else:
            where_str, where_args = sql_builder.gen_wheres_part(table, {'id': {'NOT IN': ids}})
            where_str = f'WHERE {where_str}'
            args.extend([int(item) for item in where_args])

    size = query['size'] if query.get('size', None) else 1
    args.append(int(size))
    sql = sql.replace('[WHERE]', where_str)
    resp = mysqlDB.execute(sql, args)

    if not resp['success']:
        res['code'] = status_code.StatusCode.failure,
        res['msg'] = '失败'
    else:
        res['data'] = resp['result']

    return res
