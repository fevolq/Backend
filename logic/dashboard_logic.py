#!-*- coding: utf-8 -*-
# python3.7
# CreateTime: 2023/3/13 13:20
# FileName:

from flask import request

from dao import sql_builder, mysqlDB
from status_code import StatusCode
from utils import util


def chart(query):
    current_user = request.environ['metadata.user']

    title = query.get('title', '')
    page = int(query.get('page', 1))
    page_size = int(query.get('page_size', 50))

    conditions = {'auth': {'=': current_user.email}}
    cols = ['title', 'content', 'update_at']
    if title:
        conditions['title'] = {'in': title}
    if current_user.is_super_admin():
        del conditions['auth']
        cols.append('auth')

    sql, args = sql_builder.gen_select_sql('demo', cols, condition=conditions, order_by=[('id', 'asc')],
                                           limit=page_size, offset=(page - 1) * page_size)
    count_sql, count_args = sql_builder.gen_select_sql('demo', [], count_item={'id': 'total'}, condition=conditions, )
    res = mysqlDB.execute_many([
        {'sql': sql, 'args': args},
        {'sql': count_sql, 'args': count_args},
    ])['result']

    return {'code': StatusCode.success, 'total': res[1][0]['total'], 'data': res[0]}


def test_add(query):
    current_user = request.environ['metadata.user']

    title = query['title']
    content = query['content']

    # TODO：冲突校验

    row = {
        'title': title,
        'content': content,
        'auth': current_user.email,
        'update_at': util.asia_local_time(),
    }
    sql, args = sql_builder.gen_insert_sql('demo', row, update_cols=['content', 'update_at'])
    res = mysqlDB.execute(sql, args)

    return {'code': StatusCode.success}


def test_update(query):
    return {'code': StatusCode.success}


def test_remove(query):
    return {'code': StatusCode.success}
