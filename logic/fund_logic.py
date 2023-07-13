#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/6/29 15:59
# FileName:

import json

from flask import request

from status_code import StatusCode
from dao import sql_builder, mysqlDB
from utils import util
from model.user import User


def get_option(data: dict, option_type):
    def get_rate_option():
        dates = (3, -3, 7, -7, 15, -15, 30, -30)
        option_ = {}
        for date in dates:
            if str(date) not in data or data[str(date)] is None or str(data[str(date)]) == '':
                continue
            option_[str(date)] = float(data[str(date)])
        return option_

    def get_worth_option():
        return {
            'cost': float(data['cost']),
            'worth': float(data['worth']) if data.get('worth') else None,
            'growth': float(data['growth']) if data.get('growth') else None,
            'lessen': float(data['lessen']) if data.get('lessen') else None,
        }

    option_types = {
        'rate': get_rate_option,
        'worth': get_worth_option,
    }
    assert option_type in option_types
    return option_types[option_type]()


def add_monitor(query):
    result = {
        'code': StatusCode.success,
    }
    current_user: User = request.environ['metadata.user']

    monitor_type = query['type'].lower()
    fund_code = query['code']
    assert fund_code

    option = get_option(query['option'], monitor_type)
    if not option:
        result['code'] = StatusCode.is_conflict
        return result

    row = {
        'uid': current_user.uid,
        'code': fund_code,
        'type': monitor_type,
        'option': json.dumps(option, indent=4, sort_keys=True),
        'update_at': util.asia_local_time(),
        'remark': query.get('remark')
    }
    sql, args = sql_builder.gen_insert_sql('fund_monitor', row)
    res = mysqlDB.execute(sql, args)
    if not res['success']:
        result['code'] = StatusCode.failure

    return result


def get_monitor(query):
    result = {
        'code': StatusCode.success,
    }
    current_user: User = request.environ['metadata.user']

    page = int(query.get('page', 1))
    page_size = int(query.get('page_size', 20))
    conditions = {'uid': {'=': current_user.uid}}
    if query.get('codes'):
        codes = [str(code).strip() for code in query['codes'].split(',')]
        conditions['code'] = {'in': codes}
    if query.get('type'):
        conditions['type'] = {'=': query['type'].lower()}

    sql, args = sql_builder.gen_select_sql('fund_monitor', ['id', 'code', 'option', 'type', 'update_at', 'remark'],
                                           condition=conditions, order_by=[('update_at', 'DESC')],
                                           limit=page_size, offset=(page - 1)*page_size)
    count_sql, count_args = sql_builder.gen_select_sql('fund_monitor', [],
                                                       count_item={'id': 'total'}, condition=conditions)
    res = mysqlDB.execute_many([{'sql': sql, 'args': args}, {'sql': count_sql, 'args': count_args}])['result']
    result['total'] = res[1][0]['total']
    records = res[0]
    if records:
        codes = [row['code'] for row in records]

        # TODO: 可替换成实时api请求
        name_sql, name_args = sql_builder.gen_select_sql('fund', ['code', 'name'], condition={'code': {'in': codes}})
        name_res = mysqlDB.execute(name_sql, name_args, db_name='spider')['result']
        names = {item['code']: item['name'] for item in name_res}

        for row in records:
            row['option'] = json.loads(row['option'])
            row['name'] = names.get(row['code'])
    result['data'] = records

    return result


def update_monitor(query):
    result = {
        'code': StatusCode.success,
    }
    current_user: User = request.environ['metadata.user']

    row_id = query['id']
    record_sql, record_args = sql_builder.gen_select_sql('fund_monitor', ['uid', 'update_at', 'type', 'remark'],
                                                         condition={'id': {'=': row_id}}, limit=1)
    record_res = mysqlDB.execute(record_sql, record_args)['result']
    if not record_res:
        result['code'] = StatusCode.is_conflict
        return result

    # TODO：冲突校验
    record = record_res[0]
    if record['uid'] != current_user.uid or record['update_at'] != query['update_at']:
        result['code'] = StatusCode.is_conflict
        return result

    option = get_option(query['option'], record['type'])
    row = {
        'option': json.dumps(option, indent=4, sort_keys=True),
        'update_at': util.asia_local_time(),
        'remark': query.get('remark', record['remark'])
    }
    sql, args = sql_builder.gen_update_sql('fund_monitor', row,
                                           conditions={'id': {'=': row_id}, 'update_at': {'=': record['update_at']}})
    res = mysqlDB.execute(sql, args)
    if not res['success']:
        result['code'] = StatusCode.failure
    return result


def del_monitor(query):
    result = {
        'code': StatusCode.success,
    }
    current_user: User = request.environ['metadata.user']

    condition = {
        'id': {'=': query['id']},
        'uid': {'=': current_user.uid},
        'update_at': {'=': query['update_at']}
    }
    sql, args = sql_builder.gen_delete_sql('fund_monitor', conditions=condition)
    res = mysqlDB.execute(sql, args)
    if not all(res.values()):
        result['code'] = StatusCode.is_conflict

    return result
