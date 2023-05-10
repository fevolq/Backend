#!-*coding:utf-8 -*-
# python3.7
# CreateTime: 2023/2/22 10:57
# FileName:

from flask import Blueprint, request, jsonify

from logic import template_logic

template_route = Blueprint('template', __name__)


@template_route.route('info', methods=['GET', 'POST'])
def template():
    res = template_logic.info(request)
    return jsonify(res)
