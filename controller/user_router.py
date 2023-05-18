#!-*- coding: utf-8 -*-
# python3.7
# CreateTime: 2023/3/11 20:16
# FileName:

from flask import Blueprint, request, jsonify

from logic import user_logic
from model.bean import user_util

user_route = Blueprint('user', __name__)


@user_route.route('register', methods=['POST'])
def register():
    query = request.form
    res = user_logic.register(query)
    return jsonify(res)


@user_route.route('login', methods=['POST'])
def login():
    query = request.form
    res = user_logic.login(query)
    return jsonify(res)


@user_route.route('info', methods=['GET'])
def info():
    res = user_logic.info()
    return jsonify(res)


# 更新用户信息
@user_route.route('update', methods=['PUT'])
def update():
    query = request.json
    res = user_logic.update(query)
    return jsonify(res)


# 查询用户
@user_route.route('list', methods=['GET'])
@user_util.is_admin
def users_info():
    query = request.args
    res = user_logic.users_info(query)
    return jsonify(res)


# 封禁
@user_route.route('ban', methods=['PUT'])
@user_util.is_admin
def ban():
    query = request.json
    res = user_logic.ban(query)
    return jsonify(res)
