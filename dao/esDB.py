#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2022/12/13 11:18
# FileName:

import exceptions
from dao import poolDB, db
import config


class Elasticsearch:

    def __init__(self, db_conf, use_pool) -> None:
        if use_pool:
            self.__conn = poolDB.get_coon(mode='elasticsearch', db_conf=db_conf)
        else:
            self.__conn = db.Db('elasticsearch', db_conf=db_conf)

    @property
    def coon(self):
        return self.__conn

    def execute(self, index_name: str, action: str, *args, **kwargs):
        """

        :param index_name: 指定的索引
        :param action: 执行的命令
        :param args:
        :param kwargs:
        :return:
        """
        raise_error = kwargs.pop('raise_error') if 'raise_error' in kwargs else True  # 是否扔出异常

        res = {'result': None, 'success': True}
        with self.__conn as coon:
            try:
                result = getattr(coon, action)(index=index_name, *args, **kwargs)
                res['result'] = result
            except Exception as e:
                res['result'] = e
                res['success'] = False
                if raise_error:
                    raise exceptions.DbException(e)

        return res


def execute(
    index_name: str, action: str, *args,
    db_conf: dict = None,
    use_pool=False, **kwargs,
):
    if db_conf is None:
        db_conf = {
            'host': config.ES_HOST,
            'port': config.ES_PORT,
            'user': config.ES_USER,
            'password': config.ES_PWD,
        }
    es = Elasticsearch(db_conf, use_pool)
    return es.execute(index_name, action, *args, **kwargs)


if __name__ == '__main__':
    # result = execute('demo', 'index', {'name': 'test_01'})
    # print(result)
    ...
