#!-*- coding: utf-8 -*-
# python3.7
# CreateTime: 2023/3/13 13:18
# FileName:

from flask import Blueprint, request, jsonify

from logic import dashboard_logic
from model.bean import user_util

dashboard_route = Blueprint('dashboard', __name__)


@dashboard_route.route('chart', methods=['GET'])
@user_util.has_permission('demo01.chart:table01')
def chart():
    query = request.args
    res = dashboard_logic.chart(query)
    return jsonify(res)


@dashboard_route.route('add', methods=['POST'])
@user_util.has_permission('demo01.func:demo01/add')
def test_add():
    query = request.json
    res = dashboard_logic.test_add(query)
    return jsonify(res)


@dashboard_route.route('update', methods=['PUT'])
@user_util.has_permission('demo01.func:demo01/update')
def test_update():
    query = request.json
    res = dashboard_logic.test_update(query)
    return jsonify(res)


@dashboard_route.route('remove', methods=['DELETE'])
@user_util.has_permission('demo01.func:demo01/remove')
def test_remove():
    query = request.json
    res = dashboard_logic.test_remove(query)
    return jsonify(res)

