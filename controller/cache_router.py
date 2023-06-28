#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/6/28 10:44
# FileName:

from flask import Blueprint, request, jsonify

from logic import cache_logic

cache_route = Blueprint('cache', __name__)


@cache_route.route('del', methods=['POST'])
def del_cache():
    query = request.json
    res = cache_logic.del_cache(query)
    return jsonify(res)
