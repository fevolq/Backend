#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/24 17:21
# FileName:

from flask import Blueprint, request, jsonify

from logic import dashboard_logic

dashboard_route = Blueprint('dashboard', __name__)


@dashboard_route.route('config', methods=['GET'])
def dashboard_config():
    query = dict(request.args)
    res = dashboard_logic.dashboard_config(query)
    return jsonify(res)


@dashboard_route.route('chart', methods=['POST'])
def chart():
    query = request.json
    res = dashboard_logic.chart(query)
    return jsonify(res)
