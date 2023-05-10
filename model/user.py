#!-*- coding: utf-8 -*-
# python3.7
# CreateTime: 2023/3/11 20:19
# FileName:

from typing import List

import constant
from dao import mysqlDB, sql_builder
from model.role import Role
from utils import dict_to_obj, pools


class User:

    def __init__(self, uid=None, email=None, fill_permission=True):
        # 基础元素
        self.uid = uid
        self.name = None
        self.email = email
        self.salt = None
        self.bcrypt_str = None
        self.is_ban = 0
        self.create_at = None
        self.update_at = None
        self.update_by = None
        self.remark = None

        # 衍生元素
        self.login = False

        # 权限元素
        self.roles: List[Role] = []
        self.permissions = []

        self._init(fill_permission)

    def _init(self, fill_permission=True):
        cols = ['uid', 'name', 'email', 'salt', 'bcrypt_str', 'is_ban', 'create_at', 'update_at', 'update_by', 'remark']
        condition = {}
        if self.uid is not None:
            condition['uid'] = {'=': self.uid}
        if self.email is not None:  # 登录校验
            condition['email'] = {'=': self.email}
        if not condition:
            # condition = {'id': {'=': -1}}
            return

        info_sql, info_args = sql_builder.gen_select_sql(constant.UserTable, cols, condition=condition, limit=1)
        res = mysqlDB.execute(info_sql, info_args, log_key='用户信息')['result']
        if not res:
            return

        dict_to_obj.set_obj_attr(self, res[0])
        self.login = True

        if fill_permission:
            self.load_permission()

    def load_permission(self):
        role_sql = f'SELECT {constant.RoleTable}.role_id AS role_id, {constant.RoleTable}.name AS role_name ' \
                   f'FROM {constant.RoleTable}' \
                   f' LEFT JOIN {constant.UserRoleTable} ON {constant.UserRoleTable}.role_id = {constant.RoleTable}.role_id ' \
                   f'WHERE {constant.UserRoleTable}.uid = %s'
        roles_res = mysqlDB.execute(role_sql, [self.uid], log_key='用户角色')['result']
        if roles_res:
            args = [[(role_data['role_id'],)] for role_data in roles_res]
            roles = pools.execute_event(lambda role_id: Role(role_id, fill_permission=False), args)
            self.roles = list(filter(lambda role: role.name, roles))

        if self.is_admin():     # 管理员不用再查询权限
            return
        self.permissions = self.get_permissions()

    @classmethod
    def has_register(cls, email):
        sql = f'SELECT uid FROM {constant.UserTable} WHERE email = %s LIMIT 1'
        res = mysqlDB.execute(sql, [email], log_key='注册校验')['result']
        return res

    # 用户自己可查看的信息
    def ui_info(self):
        return {
            'uid': self.uid,
            'uname': self.name,
            'email': self.email,

            'roles': [role.ui_info() for role in self.roles] if self.roles else [],
            'permissions': self.permissions,
        }

    # 管理员可查看的用户信息
    def info(self):
        return {
            'uid': self.uid,
            'uname': self.name,
            'email': self.email,
            'is_ban': self.is_ban,
            'update_at': self.update_at,
            'update_by': self.update_by,
            'remark': self.remark,

            'roles': [role.ui_info() for role in self.roles] if self.roles else [],
            'permissions': self.permissions,
        }

    def is_super_admin(self):
        return constant.SuperAdminRoleID in [role.role_id for role in self.roles]

    def is_admin(self, only_admin=False):
        check_roles = [constant.AdminRoleID] if only_admin else [constant.SuperAdminRoleID, constant.AdminRoleID]
        return set(check_roles) & set([role.role_id for role in self.roles])

    @classmethod
    def user_is_super_admin(cls, uid):
        """
        校验指定用户是否为超管
        :param uid:
        :return:
        """
        op = '='
        if isinstance(uid, list):
            op = 'IN'
        sql, args = sql_builder.gen_select_sql(constant.UserRoleTable, ['role_id'], condition={'uid': {op: uid}})
        res = mysqlDB.execute(sql, args)['result']
        if not res:
            return False

        return constant.SuperAdminRoleID in [role_data['role_id'] for role_data in res]

    @classmethod
    def user_is_admin(cls, uid, only_admin=False):
        """
        校验指定用户是否为管理员（超管）
        :param uid:
        :param only_admin: 仅管理员
        :return:
        """
        op = '='
        if isinstance(uid, list):
            op = 'IN'
        sql, args = sql_builder.gen_select_sql(constant.UserRoleTable, ['role_id'], condition={'uid': {op: uid}})
        res = mysqlDB.execute(sql, args, log_key='某用户角色')['result']
        if not res:
            return False

        check_roles = [constant.AdminRoleID] if only_admin else [constant.SuperAdminRoleID, constant.AdminRoleID]
        return set(check_roles) & set([role_data['role_id'] for role_data in res])

    def get_permissions(self):
        permissions = []

        args = [[(role, )] for role in self.roles]
        role_permissions = pools.execute_event(lambda role: role.get_all_permission(), args)
        for role_permission in role_permissions:
            permissions.extend(role_permission)

        return sorted(list(set(permissions)))

    def has_permission(self, permission):
        return self.is_admin() or permission in self.permissions
