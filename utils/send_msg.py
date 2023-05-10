#!-*coding:utf-8 -*-
# python3.7
# CreateTime: 2022/11/4 18:16
# FileName: 发送消息

import json
import sys
import typing

import requests

import config


def feishu_robot_msg(robot_url: str, content: typing.Union[dict, str], title=None):
    """飞书 机器人消息"""
    assert robot_url
    try:
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)

        msg = {
            'title': title,
            'content': [
                [
                    {
                        'tag': 'text',
                        'text': content
                    }
                ]
            ]
        }

        data = {
            'msg_type': 'post',
            'content': {
                'post': {
                    'zh-cn': msg
                }
            }
        }
        resp = requests.post(robot_url, json=data)
        pass
    except Exception:
        pass


class WinXin:
    """
    微信
    """

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret

        self.access_token = self.__fetch_access_token()

    def __fetch_access_token(self):
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}'
        resp = requests.get(url.format_map({'app_id': self.app_id, 'app_secret': self.app_secret}))
        if resp.status_code != 200:
            return None
        return resp.json().get('access_token')

    def send_public_msg(self, open_id: str, msg: dict, template_id):
        """
        发送公众号消息
        :param open_id: 用户ID
        :param msg: 模板数据
        :param template_id: 模板ID
        :return:
        """
        assert self.access_token

        url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={self.access_token}'
        for key in msg.keys():
            if not isinstance(msg[key], dict):
                msg[key] = {'value': msg[key]}
        data = {
            'touser': open_id,
            'template_id': template_id,
            'data': msg
        }
        resp = requests.post(url, json=data)
        pass


class ServerChan:
    """Server酱"""
    def __init__(self, key):
        self.key = key

    @classmethod
    def __check_length(cls, value, max_len):
        if not value:
            return
        if isinstance(value, str):
            assert len(value) < max_len
        elif isinstance(value, int):
            assert value < max_len

    def send_msg(self, title, content='', short=None):
        """

        :param title:
        :param content:
        :param short:
        :return:
        """
        check = [
            {'value': title, 'max': 32},
            {'value': sys.getsizeof(title.encode('utf-8')), 'max': 32 * 1024},      # 32KB
            {'value': short, 'max': 64},
        ]
        for item in check:
            self.__check_length(item['value'], item['max'])

        url = f'https://sctapi.ftqq.com/{self.key}.send'

        data = {
            'title': title,
            'short': short,
            'desp': content,
        }
        resp = requests.post(url, data)
        pass


def weixin_public_msg(open_id: str, msg: dict, **options):
    """
    微信公众号消息
    :param open_id:
    :param msg:
    :param options:
    :return:
    """
    app_id = options.get('app_id', config.WxAppId)
    app_secret = options.get('app_secret', config.WxAppSecret)
    template_id = options.get('template_id', config.WxTemplateId)
    return WinXin(app_id, app_secret).send_public_msg(open_id, msg, template_id)


def chan_msg(title, content='', short=None, **options):
    key = options.get('key', config.ChanKey)
    return ServerChan(key).send_msg(title, content=content, short=short)


if __name__ == '__main__':
    info_ = 'hello world\nhttps://www.baidu.com'
    url_ = ''
    feishu_robot_msg(url_, info_, title='test')
