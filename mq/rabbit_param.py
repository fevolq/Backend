#!-*- coding:utf-8 -*-
# python3.7
# CreateTime: 2023/3/27 16:11
# FileName: rabbitmq参数模式

import json

import pika

import config


class RabbitMQ:

    host = config.RABBIT_HOST
    port = config.RABBIT_PORT
    username = config.RABBIT_USER
    password = config.RABBIT_PWD

    def __init__(self, queue_name, **options):
        self.queue_name = queue_name

        self.prefetch_count = options.get('prefetch_count', 1)      # 默认公平分发
        self.durable = options.get('durable', True)             # 默认持久化
        self.auto_ack = options.get('auto_ack', False)         # 默认手动应答

        self.coon = None
        self.channel = None
        self._prepare()

    def _prepare(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        options = {
            'host': self.host,
            'port': self.port,
            'virtual_host': '/',
        }
        if self.username:
            options.update({'credentials': credentials})
        self.conn = pika.BlockingConnection(pika.ConnectionParameters(**options))
        self.channel = self.conn.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=self.durable)
        self.channel.basic_qos(prefetch_count=self.prefetch_count)
        self.channel.confirm_delivery()         # 确认消息已发送，避免一些消息未发送到队列，主程序便已结束

    def start_consuming(self, func):
        def callback(ch, method, propertes, body):
            data = json.loads(body.decode())
            func(**data)
            if not self.auto_ack:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        print(f'{self.queue_name} 开始监听...')
        self.channel.basic_consume(
            queue=self.queue_name,
            auto_ack=self.auto_ack,
            on_message_callback=callback,
        )
        self.channel.start_consuming()

    def send_msg(self, data: dict):
        """
        发送消息
        :param data: 必须为键值对
        :return:
        """
        assert isinstance(data, dict)
        self.channel.basic_publish(
            exchange='',        # 简单模式
            routing_key=self.queue_name,
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=2 if self.durable else 1,  # 指定该信息为持久化保存，其他值为瞬态（即不持久化）
                content_type='application/json',
            )
        )
        # return self.channel.wait_for_confirms()      # 可等待确认消息
