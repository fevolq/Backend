#!-*- coding: utf-8 -*-
# python3.7
# CreateTime: 2023/3/11 21:42
# FileName:

import json
from typing import List

from flask import request

import constant
from dao import sql_builder, mysqlDB
from model.role import Role
from status_code import StatusCode
from utils import util


def add_role(query):
    """
    角色默认直接添加，可继承多个角色。
    :param query:
    :return:
    """
    current_user = request.environ['metadata.user']

    name = query['name']
    remark = query.get('remark')
    parent: List = query.get('parent', [])
    current_time = util.asia_local_time()
    row = {
        'role_id': util.gen_unique_str(name),
        'name': name,
        'parent': parent if parent else None,
        'remark': remark,
        'create_at': current_time,
        'update_at': current_time,
        'create_by': current_user.email,
    }
    sql, args = sql_builder.gen_insert_sql(constant.RoleTable, row)
    res = mysqlDB.execute(sql, args)
    Role.clear_all_data()
    return {'code': StatusCode.success}


def remove_role(query):
    role_ids = query['role_ids']
    assert not set(role_ids) & set([constant.SuperAdminRoleID, constant.AdminRoleID, constant.DefaultRoleID])

    # TODO：冲突校验

    sql, args = sql_builder.gen_delete_sql(constant.RoleTable, conditions={'role_id': {'IN': role_ids}})
    res = mysqlDB.execute(sql, args)
    Role.clear_all_data()
    return {'code': StatusCode.success}


def update_role(query):
    current_user = request.environ['metadata.user']
    data = query['data']
    role_id = query['role_id']
    assert role_id not in [constant.SuperAdminRoleID, constant.AdminRoleID, constant.DefaultRoleID]

    # TODO：冲突校验

    can_change_fields = ['name', 'remark', 'parent']
    change_fields = {field: data[field] for field in can_change_fields if field in data}
    if not change_fields:
        return {'code': StatusCode.success}
    elif 'parent' in change_fields:
        all_role_ids = [role_data['role_id'] for role_data in Role.get_all_data()]
        for parent_id in change_fields['parent']:
            assert parent_id in all_role_ids
            assert parent_id not in [constant.SuperAdminRoleID, constant.AdminRoleID, constant.DefaultRoleID]
        change_fields['parent'] = json.dumps(change_fields['parent'])

    change_fields['update_at'] = util.asia_local_time()
    change_fields['update_by'] = current_user.email

    sql, args = sql_builder.gen_update_sql(constant.RoleTable, change_fields,
                                           conditions={'role_id': {'=': role_id}})
    res = mysqlDB.execute(sql, args)
    Role.clear_all_data()
    return {'code': StatusCode.success}


def info(query):
    role_id = query.get('role_id', None)
    role_name = query.get('role_name', None)

    all_role_data = {role_data['role_id']: role_data for role_data in Role.get_all_data()}
    role_id_set = set(list(all_role_data.keys()))
    if role_id:
        role_id_set = role_id_set & set([role_id])
    if role_name:
        sql, args = sql_builder.gen_select_sql(constant.RoleTable, ['role_id'], condition={'name': {'LIKE': role_name}},
                                               order_by=[('id', 'asc')])
        res = mysqlDB.execute(sql, args)['result']
        role_id_set = role_id_set & set([row['role_id'] for row in res])

    roles = (Role(role_id_) for role_id_ in sorted(list(role_id_set), key=lambda role_id_: all_role_data[role_id_]['id']))
    return {'code': StatusCode.success, 'data': [role.info() for role in roles]}
