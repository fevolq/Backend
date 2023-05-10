#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/10 10:23
# FileName:

from .app_config import *
from .db_config import *
from .mq_config import *
from .other_config import *


# 从系统环境中重载变量
for var, var_value in locals().copy().items():
    # 变量命名要求全大写，不能以“_”开头
    if var.startswith('_') or callable(var_value) or not var[0].isupper():
        continue

    locals()[var] = os.getenv(var, var_value)


try:
    from .local_config import *
except:
    pass
