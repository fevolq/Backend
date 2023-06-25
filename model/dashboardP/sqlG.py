#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/31 16:14
# FileName: sql生成器

from dao import sql_builder
from utils.dict_to_obj import DictToObj


class SqlGenerator:

    def __init__(self, chart):
        self.__chart = chart

        self.__select: DictToObj = None
        self.__from: DictToObj = None
        self.__join: DictToObj = None
        self.__where: DictToObj = None
        self.__group_by: DictToObj = None
        self.__order_by: DictToObj = None
        self.__limit: DictToObj = None

    def gen(self):
        self.__gen_select()
        self.__gen_from()
        self.__gen_where()
        self.__gen_group_by()
        self.__gen_order_by()
        self.__gen_limit()
        self.__gen_join()       # 必须在最后（需要获取所有使用的字段）

        sql = f'{self.__select.value} {self.__from.value} {self.__join.value} {self.__where.value}' \
              f' {self.__group_by.value} {self.__order_by.value} {self.__limit.value}'
        args = self.__where.args
        return sql, args

    def __gen_select(self):
        select = dict([('value', '')])

        cols = {col_name: self.__chart.all_cols[col_name] for col_name in [*self.__chart.rows, *self.__chart.cols]}
        cols.update({col.name: col for col in self.__chart.get_expand_filter_cols().values()})
        select['cols'] = cols
        value = ', '.join([f'{self.__chart.dataset.get_field_value_in_sql(chart_col.field)} AS {chart_col.alias}'
                           for _, chart_col in cols.items()])
        select['value'] = f'SELECT {value}'

        self.__select = DictToObj(select)

    def __gen_from(self):
        from_ = dict([('value', '')])
        dataset = self.__chart.dataset
        if dataset.sql:
            from_['value'] = f'FROM ({dataset.sql}) AS `{dataset.table}`'
        else:
            from_['value'] = f'FROM `{dataset.table}`'

        self.__from = DictToObj(from_, 'from')

    def __gen_join(self):
        joins = dict([('value', '')])

        joins_value = [join.value() for join in self.__chart.dataset.get_joins()]
        joins['value'] = ' '.join(joins_value)

        self.__join = DictToObj(joins, 'join')

    def __gen_where(self):
        where = dict([('value', '')])

        wheres = []
        args = []
        for col_name, condition in self.__chart.conditions.items():
            col_expr = self.__chart.dataset.get_field_value_in_sql(self.__chart.all_cols[col_name].field)
            where_str, where_args = sql_builder.gen_wheres_part('', {col_expr: condition})
            wheres.append(f'({where_str})')
            args.extend(where_args)

        where['args'] = args
        if wheres:
            where['value'] = f'WHERE {" AND ".join(wheres)}'

        self.__where = DictToObj(where, 'where')

    def __gen_group_by(self):
        group_by = dict([('value', '')])
        group_by['cols'] = cols = self.__chart.get_dim_cols()
        value = ', '.join([self.__chart.dataset.get_field_value_in_sql(chart_col.field) for _, chart_col in cols.items()])
        if cols:
            group_by['value'] = f'GROUP BY {value}'

        self.__group_by = DictToObj(group_by, 'group by')

    def __gen_order_by(self):
        order_by = dict([('value', '')])
        order_by['cols'] = cols = {col_name: self.__chart.all_cols[col_name] for col_name in self.__chart.sorts}

        values = []
        for _, chart_col in cols.items():
            mod = 'DESC' if chart_col.order else 'ASC'
            values.append(f'{self.__chart.dataset.get_field_value_in_sql(chart_col.field)} {mod}')

        if values:
            order_by['value'] = f'ORDER BY {", ".join(values)}'

        self.__order_by = DictToObj(order_by, 'order_by')

    def __gen_limit(self):
        limit = dict([('value', '')])
        limit['value'] = f'LIMIT {self.__chart.limit}'

        self.__limit = DictToObj(limit, 'limit')
