#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/10 10:45
# FileName:

from . import (
    template_router,
    poem_router,
)

blueprint = {
    # url_prefix: blueprint
    'template': template_router.template_route,
    'poem': poem_router.poem_route,
}
