#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/10 10:45
# FileName:

from . import (
    template_router,
    user_router,
    role_router,
    permission_router,
    poem_router,
    dashboard_router,
    cache_router,
)

blueprint = {
    # url_prefix: blueprint
    'template': template_router.template_route,
    'user': user_router.user_route,
    'role': role_router.role_route,
    'permission': permission_router.permission_route,
    'poem': poem_router.poem_route,
    'dashboard': dashboard_router.dashboard_route,
    'cache': cache_router.cache_route,
}
