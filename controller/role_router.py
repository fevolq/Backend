#!-*- coding: utf-8 -*-
# python3.7
# CreateTime: 2023/3/11 21:40
# FileName:

from flask import Blueprint, request, jsonify

from logic import role_logic
from model.bean import user_util

role_route = Blueprint('role', __name__)


@role_route.route('add', methods=['POST'])
@user_util.is_admin
def add_role():
    query = request.json
    res = role_logic.add_role(query)
    return jsonify(res)


@role_route.route('remove', methods=['DELETE'])
@user_util.is_admin
def remove_role():
    query = request.json
    res = role_logic.remove_role(query)
    return jsonify(res)


@role_route.route('update', methods=['PUT'])
@user_util.is_admin
def update_role():
    query = request.json
    res = role_logic.update_role(query)
    return jsonify(res)


@role_route.route('info', methods=['GET'])
@user_util.is_admin
def info():
    query = request.args
    res = role_logic.info(query)
    return jsonify(res)
