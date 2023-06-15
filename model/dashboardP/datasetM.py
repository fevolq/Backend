#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/27 15:36
# FileName:

import copy
from typing import List
import re

from model.dashboardP.util import read


class Dataset:

    def __init__(self, name):
        self._config = read(('dataset', name))

        self.name = name
        self.title = self._config.get('title', None)
        self.db = self._config.get('db', None)
        self.table = self._config['table']
        self.sql = self._config.get('sql', None)
        self.fields: dict = {field_name: Field(field_name, field_config)
                             for field_name, field_config in self._config.get('fields', {}).items()}
        self._joins: {str: Join} = {}

        self._use_fields = {}       # 生成chart视图时使用到的所有字段
        self.__inflate()

    def __repr__(self):
        return f'{self.name}[{self.title}]'

    def __inflate(self):
        for item in self._config.get('joins', []):
            join = Join(item.get('root_table', self.table), item)
            self._joins[join.table] = join
            self._joins[join.name] = join

    def get_field_value_in_sql(self, field) -> str:
        """
        获取指定 field 在sql语句中的写值
        :param field:
        :return:
        """
        if field is None:
            return ''
        self._use_fields[field.name] = field

        def load_field_type(field_type, value):
            if field_type == 'DATE':
                return f'DATE({value})'
            return value

        if field.expr is None:
            if field.name.find('.') > 0:
                return load_field_type(field.type, field.name)
            else:
                return load_field_type(field.type, f'`{self.table}`.`{field.name}`')

        def get_expr_field(value):
            if value == 1:      # 仅充作占位符
                return value

            re_pattern = re.compile(r'\[(.*?)\]')
            groups = re_pattern.findall(value)
            for group in groups:
                value = value.replace(f'[{group}]', self.get_field_value_in_sql(self.fields.get(group)))
            return value

        return get_expr_field(field.expr)

    def get_joins(self):
        # 所有使用到的表
        tables = set()
        for field_name, _ in self._use_fields.items():
            table = self.table if field_name.find('.') < 0 else field_name.split('.')[0]
            tables.add(table)

        # 表对应的 join 节点
        joins = [self._joins[table] for table in tables if table != self.table]

        # 所有应参加的 join 节点（包括间接连接）
        join_nodes = {}

        def add_join_node(node: Join):
            join_nodes[node.name] = node
            if node.root_table != self.table:
                add_join_node(self._joins[node.root_table])

        for join in joins:
            add_join_node(join)

        # 节点分层（JOIN 顺序有要求）
        result_joins = []
        nodes_name = list(join_nodes.keys())
        parent_nodes_name = {self.table}
        while len(nodes_name) > 0:
            hint_index = []
            for index, node_name in enumerate(nodes_name):
                join_node: Join = join_nodes[node_name]
                if join_node.root_table in parent_nodes_name:
                    result_joins.append(join_node)
                    hint_index.append(index)
            if not hint_index:
                raise Exception(f'Dataset[{self.name}] 存在无法join的表')

            parent_nodes_name = set([nodes_name[index] for index in hint_index])
            for index in hint_index[::-1]:
                nodes_name.pop(index)
        return result_joins

    def expand_field(self, mod, **kwargs):
        if mod == '*':
            self.__expand_field_star(**kwargs)
        elif mod == 'step':
            self.__expand_field_step(**kwargs)
        elif mod == 'kwargs':
            self.__expand_field_args(**kwargs)
        pass

    def __expand_field_star(self, **kwargs):
        """
        扩充 table.* 字段
        :param kwargs:
        :return:
        """
        col_name = kwargs['col_name']
        field_name = f'{col_name.split(".")[0]}.*'
        field = Field(col_name, self.fields[field_name].config)
        self.fields[field.name] = field

    def __expand_field_step(self, **kwargs):
        """
        扩充 field{expand} 字段
        :param kwargs:
        :return:
        """
        change_items = ['label', 'expr']
        replace_item = '{expand}'

        def format_step(field_conf, args):
            for item in change_items:
                if item not in field_conf:
                    continue
                field_conf[item] = field_conf[item].replace(replace_item, str(args))

        col_name = kwargs['col_name']
        for value in kwargs['args']:
            field_config = copy.deepcopy(self.fields[col_name].config)
            new_field_name = col_name.replace(replace_item, str(value))
            format_step(field_config, value)
            field = Field(new_field_name, field_config)
            self.fields[new_field_name] = field

    def __expand_field_args(self, **kwargs):
        """
        扩充 field{i}{j} 字段
        :param kwargs:
        :return:
        """
        def format_args(item_value, options):
            for k, v in options.items():
                if isinstance(item_value, str):
                    item_value = item_value.replace(f'{{{k}}}', f'{v}')
                elif isinstance(item_value, list):
                    tmp_item_value = []
                    for value in item_value:
                        value = value.replace(f'{{{k}}}', f'{v}')
                        tmp_item_value.append(value)
                    item_value = tmp_item_value
            return item_value

        col_name = kwargs['col_name']

        change_items = ['label', 'expr']
        for args in kwargs['kwargs']:
            field_config = copy.deepcopy(self.fields[col_name].config)
            for item in change_items:
                if item not in field_config:
                    continue

                field_config[item] = format_args(field_config[item], args)
            new_field_name = format_args(col_name, args)
            field = Field(new_field_name, field_config)
            self.fields[new_field_name] = field

    @staticmethod
    def set_fields_alias(fields: List, *args):
        for field in fields:
            field.set_alias(*args)


class Field:

    def __init__(self, name, config):
        self.name = name
        self._config = config

        self.label = self._config.get('label', None)
        self.type = self._config.get('type', None)
        self.expr = self._config.get('expr', None)
        self.extra = self._config.get('extra', {})
        self.__alias = self.name

    def __repr__(self):
        return f'{self.name}[{self.label}]'

    @property
    def config(self):
        return self._config

    def set_alias(self, *args):
        # 取第一个有效值
        for value in args:
            if value:
                self.__alias = f'{value}_{self.__alias}'
                break

    @property
    def alias(self):
        self.__alias = self.__alias.replace('.', '_')
        return self.__alias


class Join:
    """
    {
        type: 连接方式,
        table: 连接的表,
        as: 别名。可选,
        root_table: 主表。可选，默认 dataset 定义的表,
        on: {
            field: 连接的字段,
            root_field: 主表的字段。与 field 同名时可选
        }
    }
    """

    def __init__(self, root_table, join_config):
        self._config = join_config

        self.root_table = root_table
        self.type = join_config['type'].upper()
        self.table = join_config['table']
        self.alias = join_config.get('as')
        self.field = join_config['on']['field']
        self.root_field = join_config['on'].get('root_field', self.field)

    def __repr__(self):
        return self.name

    @property
    def name(self):
        return self.alias or self.table

    def value(self):
        table = f'{self.table} AS {self.alias}' if self.alias else self.table
        field = f'`{self.name}`.`{self.field}`'
        return f'{self.type} JOIN {table} ON {field} = `{self.root_table}`.`{self.root_field}`'
