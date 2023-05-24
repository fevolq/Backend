#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/10 10:45
# FileName:

from . import (
    template_router,
    dashboard_router,
)

blueprint = {
    # url_prefix: blueprint
    'template': template_router.template_route,
    'dashboard': dashboard_router.dashboard_route,
}
