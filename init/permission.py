#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/6/26 12:41
# FileName: 权限控制初始化

import configparser

import constant
from dao import mysqlDB, sql_builder
from model.bean import user_util
from utils import util


class Table:

    """表创建"""

    def __init__(self): ...

    @staticmethod
    def user_table_sql():
        init_sql_1 = 'SET NAMES utf8mb4;'
        init_sql_2 = 'SET FOREIGN_KEY_CHECKS = 0;'
        drop_sql = f'DROP TABLE IF EXISTS `{constant.UserTable}`;'
        create_sql = f"""CREATE TABLE `{constant.UserTable}`  (
                      `id` int NOT NULL AUTO_INCREMENT,
                      `uid` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户ID',
                      `name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                      `email` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                      `salt` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '盐',
                      `bcrypt_str` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                      `is_ban` tinyint(1) UNSIGNED ZEROFILL NOT NULL DEFAULT 0 COMMENT '是否封禁',
                      `create_at` timestamp NOT NULL COMMENT '创建时间',
                      `update_at` timestamp NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                      `update_by` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '更新人的邮箱',
                      `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注',
                      PRIMARY KEY (`id`) USING BTREE,
                      UNIQUE INDEX ```uid```(`uid`) USING BTREE,
                      UNIQUE INDEX `email`(`email`) USING BTREE
                    ) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;
                    """
        set_key_sql = 'SET FOREIGN_KEY_CHECKS = 1;'
        return init_sql_1, init_sql_2, drop_sql, create_sql, set_key_sql

    @staticmethod
    def role_table_sql():
        init_sql_1 = 'SET NAMES utf8mb4;'
        init_sql_2 = 'SET FOREIGN_KEY_CHECKS = 0;'
        drop_sql = f'DROP TABLE IF EXISTS `{constant.RoleTable}`;'
        create_sql = f"""CREATE TABLE `{constant.RoleTable}`  (
                      `id` int NOT NULL AUTO_INCREMENT,
                      `role_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '角色ID',
                      `name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '角色名称',
                      `parent` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '父角色',
                      `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注',
                      `create_at` timestamp NOT NULL ON UPDATE CURRENT_TIMESTAMP,
                      `update_at` timestamp NULL DEFAULT NULL,
                      `create_by` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                      `update_by` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
                      PRIMARY KEY (`id`) USING BTREE,
                      UNIQUE INDEX `name`(`name`) USING BTREE,
                      UNIQUE INDEX ```role_id```(`role_id`) USING BTREE
                    ) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;
                    """
        set_key_sql = 'SET FOREIGN_KEY_CHECKS = 1;'
        return init_sql_1, init_sql_2, drop_sql, create_sql, set_key_sql

    @staticmethod
    def user_role_table_sql():
        init_sql_1 = 'SET NAMES utf8mb4;'
        init_sql_2 = 'SET FOREIGN_KEY_CHECKS = 0;'
        drop_sql = f'DROP TABLE IF EXISTS `{constant.UserRoleTable}`;'
        create_sql = f"""CREATE TABLE `{constant.UserRoleTable}`  (
                      `id` int NOT NULL AUTO_INCREMENT,
                      `uid` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                      `role_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                      `update_at` timestamp NOT NULL ON UPDATE CURRENT_TIMESTAMP,
                      `update_by` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                      PRIMARY KEY (`id`) USING BTREE,
                      INDEX ```uid```(`uid`) USING BTREE,
                      UNIQUE INDEX `unique`(`uid`, `role_id`) USING BTREE,
                      INDEX ```role_id```(`role_id`) USING BTREE
                    ) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;
                    """
        set_key_sql = 'SET FOREIGN_KEY_CHECKS = 1;'
        return init_sql_1, init_sql_2, drop_sql, create_sql, set_key_sql

    @staticmethod
    def role_permission_table_sql():
        init_sql_1 = 'SET NAMES utf8mb4;'
        init_sql_2 = 'SET FOREIGN_KEY_CHECKS = 0;'
        drop_sql = f'DROP TABLE IF EXISTS `{constant.RolePermissionTable}`;'
        create_sql = f"""CREATE TABLE `{constant.RolePermissionTable}`  (
                      `id` int NOT NULL AUTO_INCREMENT,
                      `role_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
                      `permission` varchar(5000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '权限',
                      `update_at` timestamp NOT NULL ON UPDATE CURRENT_TIMESTAMP,
                      `update_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '更新人邮箱',
                      PRIMARY KEY (`id`) USING BTREE,
                      UNIQUE INDEX `role_id`(`role_id`) USING BTREE
                    ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;
                    """
        set_key_sql = 'SET FOREIGN_KEY_CHECKS = 1;'
        return init_sql_1, init_sql_2, drop_sql, create_sql, set_key_sql

    @staticmethod
    def create_table(table, table_sql_list):
        for sql in table_sql_list:
            res = mysqlDB.execute(sql)
        print(f'{table} 创建成功')

    def main(self):
        tables = {
            'user': self.user_table_sql(),
            'role': self.role_table_sql(),
            'user_role': self.user_role_table_sql(),
            'role_permission': self.role_permission_table_sql(),
        }
        for table, table_sql_list in tables.items():
            self.create_table(table, table_sql_list)


class Data:

    """数据初始化"""

    def __init__(self, root_name='root', root_email='root', root_password='root', root_remark='超管'):
        self.root_uid = user_util.gen_uid()
        self.root_name = root_name
        self.root_email = root_email
        self.root_password = root_password
        self.root_remark = root_remark

        self.super_admin_role_id = None

    @staticmethod
    def truncate_table(table):
        sql_list = [
            f'TRUNCATE TABLE {table};',
            f'ALTER TABLE {table} AUTO_INCREMENT = 1;',
        ]
        for sql in sql_list:
            mysqlDB.execute(sql)

    def create_root_user(self):
        self.truncate_table(constant.UserTable)

        salt = user_util.gen_salt()
        bcrypt_str = user_util.gen_bcrypt_str(self.root_password, salt)
        current_time = util.asia_local_time()
        data = {
            'uid': self.root_uid,
            'name': self.root_name,
            'email': self.root_email,
            'salt': salt,
            'bcrypt_str': bcrypt_str,
            'create_at': current_time,
            'update_at': current_time,
            'remark': self.root_remark,
        }
        sql, args = sql_builder.gen_insert_sql(constant.UserTable, data)
        mysqlDB.execute(sql, args)

    def create_init_roles(self):
        """
        创建初始角色：超管、管理员、默认角色
        :return:
        """
        self.truncate_table(constant.RoleTable)

        def gen_role_data(name):
            current_time = util.asia_local_time()
            return {
                'role_id': util.gen_unique_str(name),
                'name': name,
                'parent': None,
                'remark': name,
                'create_at': current_time,
                'update_at': current_time,
                'create_by': self.root_email,
            }

        result = {}
        for role_name in ('超管', '管理员', '默认'):
            data = gen_role_data(role_name)
            sql, args = sql_builder.gen_insert_sql(constant.RoleTable, data)
            mysqlDB.execute(sql, args)

            record_sql, record_args = sql_builder.gen_select_sql(constant.RoleTable, ['role_id'],
                                                                 condition={'name': {'=': role_name}})
            res = mysqlDB.execute(record_sql, record_args)['result']
            result[role_name] = res[0]['role_id']
        # TODO: 重写入constant文件

        self.super_admin_role_id = result['超管']
        for role_name, role_id in result.items():
            print(f'【{role_name}】: {role_id}')

    def associate_root_user(self):
        """
        关联root用户的超管权限
        :return:
        """
        self.truncate_table(constant.UserRoleTable)

        data = {
            'uid': self.root_uid,
            'role_id': self.super_admin_role_id,
            'update_at': util.asia_local_time(),
            'update_by': self.root_email,
        }
        sql, args = sql_builder.gen_insert_sql(constant.UserRoleTable, data)
        mysqlDB.execute(sql, args)

    def main(self):
        self.create_root_user()
        self.create_init_roles()
        self.associate_root_user()


def get_config():
    options = {'table': {}, 'data': {}}
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    conf = dict(config['permission'])

    for k, v in conf.items():
        if k.startswith('data.'):
            k = '.'.join(k.split('.')[1:])
            options['data'].update({k: v})
        elif k.startswith('table.'):
            k = '.'.join(k.split('.')[1:])
            options['table'].update({k: v})
    return options


def main():
    options = get_config()
    Table().main()
    Data(**options.get('data', {})).main()


if __name__ == '__main__':
    # main()
    pass
