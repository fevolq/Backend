#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/5/22 11:06
# FileName:

from flask import Blueprint, request, jsonify

from logic import poem_logic

poem_route = Blueprint('poem', __name__)


@poem_route.route('poem', methods=['GET'])
def poem():
    query = request.args
    res = poem_logic.poem(query)
    return jsonify(res)


@poem_route.route('witticism', methods=['GET'])
def witticism():
    query = request.args
    res = poem_logic.witticism(query)
    return jsonify(res)
