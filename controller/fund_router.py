#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/6/29 15:59
# FileName:

from flask import Blueprint, request, jsonify

from logic import fund_logic
from model.bean import user_util

fund_route = Blueprint('fund', __name__)


@fund_route.route('monitor', methods=['POST'])
@user_util.is_login
def add_monitor():
    query = request.json
    res = fund_logic.add_monitor(query)
    return jsonify(res)


@fund_route.route('monitor', methods=['GET'])
@user_util.is_login
def get_monitor():
    query = dict(request.args)
    res = fund_logic.get_monitor(query)
    return jsonify(res)


@fund_route.route('monitor', methods=['PUT'])
@user_util.is_login
def update_monitor():
    query = request.json
    res = fund_logic.update_monitor(query)
    return jsonify(res)


@fund_route.route('monitor', methods=['DELETE'])
@user_util.is_login
def del_monitor():
    query = request.json
    res = fund_logic.del_monitor(query)
    return jsonify(res)
