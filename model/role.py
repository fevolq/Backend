#!-*- coding: utf-8 -*-
# python3.7
# CreateTime: 2023/3/11 21:59
# FileName:

import json
import threading
from typing import List

import constant
from dao import sql_builder, mysqlDB
from utils import dict_to_obj, pools


class Role:

    """
    若继承至其他角色，则包含该角色的权限。如：role1.parent = [role2]，则role2的权限包括role1的权限
    """

    all_data = None  # 仅包含基础元素
    __lock = threading.RLock()

    def __init__(self, role_id, fill_permission=True):
        # 基础元素
        self.role_id = role_id
        self.name = None
        self.remark = None
        self.create_at = None
        self.update_at = None
        self.create_by = None
        self.update_by = None

        # 衍生元素
        self.parent: List[Role] = []

        # 权限元素
        self.users: List[dict] = []
        self.permissions = []

        self._init(fill_permission)

    def _init(self, fill_permission=False):
        all_role_data = {role_data['role_id']: role_data for role_data in self.get_all_data()}

        # 填充属性
        role_data = all_role_data.get(self.role_id, {})
        dict_to_obj.set_obj_attr(self, role_data)

        parent = role_data.get('parent', None)
        if parent:
            # TODO：相互为父级时的处理，会造成死循环
            args_list = [[(parent_id, )] for parent_id in json.loads(parent)]
            result = pools.execute_event(lambda role_id: Role(role_id, fill_permission=fill_permission), args_list)
            self.parent = list(filter(lambda role: role.name, result))
            # 对象全局缓存

        if fill_permission:
            self.get_permission()

    def get_permission(self):
        if not self.permissions:
            # TODO: 以role_id为键，进行缓存
            permission_sql, permission_args = sql_builder.gen_select_sql(constant.RolePermissionTable, ['permission'],
                                                                         condition={'role_id': {'=': self.role_id}},
                                                                         limit=1)
            permission_res = mysqlDB.execute(permission_sql, permission_args)['result']
            if permission_res:
                self.permissions = json.loads(permission_res[0]['permission'])
        return self.permissions

    def get_role_users(self):
        if not self.users:
            user_sql = f'SELECT {constant.UserTable}.uid AS uid, {constant.UserTable}.name AS uname ' \
                       f'FROM {constant.UserTable}' \
                       f' LEFT JOIN {constant.UserRoleTable} ON {constant.UserRoleTable}.uid = {constant.UserTable}.uid ' \
                       f'WHERE {constant.UserRoleTable}.role_id = %s'
            self.users = mysqlDB.execute(user_sql, [self.role_id])['result']
        return self.users

    def ui_info(self):
        return {
            'role_id': self.role_id,
            'name': self.name,
            'remark': self.remark,
        }

    def info(self):
        return {
            'role_id': self.role_id,
            'name': self.name,
            'remark': self.remark,
            'create_at': self.create_at,
            'update_at': self.update_at,
            'create_by': self.create_by,
            'update_by': self.update_by,
            'parent': [child.info() for child in self.parent] if self.parent else None,

            'users': self.get_role_users(),
            'permissions': self.get_permission(),
        }

    @classmethod
    def get_all_data(cls):
        if cls.all_data is None:
            with cls.__lock:
                if cls.all_data:
                    return cls.all_data

                cols = ['id', 'role_id', 'name', 'remark', 'create_at', 'update_at', 'create_by', 'update_by', 'parent']
                sql, args = sql_builder.gen_select_sql(constant.RoleTable, cols)
                res = mysqlDB.execute(sql, args, log_key='角色信息')['result']
                cls.all_data = res
        return cls.all_data

    @classmethod
    def clear_all_data(cls):
        cls.all_data = None

    def get_all_permission(self):
        """
        获取角色的所有权限（包括继承的权限）
        :return:
        """
        permissions = self.get_permission()

        if self.parent:
            args = [[(parent_role,)] for parent_role in self.parent]
            parent_permissions = pools.execute_event(lambda role: role.get_all_permission(), args)
            for permission in parent_permissions:
                permissions.extend(permission)

        return list(set(permissions))
