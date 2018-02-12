#!/usr/bin/env python
import sys
sys.path.insert(0, "../lib")

import pika
from config import RabbitMQ
import uuid
import json
import logging

logging.basicConfig(filename='../logs/rpc_pub.log',level=logging.INFO, format='%(asctime)s %(message)s')

class RpcPub(object):

    '''
    RabbitMQ RPC Publisher
    '''

    def __init__(self, queue):
        self.username      = RabbitMQ.username
        self.password      = RabbitMQ.password
        self.host          = RabbitMQ.host
        self.port          = RabbitMQ.port
        self.virtual_host  = RabbitMQ.virtual_host
        self.exchange      = RabbitMQ.exchange
        self.queue         = queue

        self.connection = self.get_connection()
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.logger = logging.getLogger('rpc_pub')
        self.logger.addHandler(logging.StreamHandler())

        self.channel.basic_consume(self.on_response, no_ack=True, queue = self.callback_queue)

    def get_connection(self):
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            return pika.BlockingConnection(pika.ConnectionParameters(self.host, self.port, self.virtual_host, credentials))
        except Exception as e:
            self.logger.critical(e)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body.decode('utf-8'))

    def keep_alive(self):
        if self.connection.is_closed:
            self.connection = self.get_connection()
            self.channel = self.connection.channel()

    def call(self, data_dict):
        data_json = json.dumps(data_dict)
        print("Requesting {}".format(data_json))
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.queue,
            properties=pika.BasicProperties(
                reply_to = self.callback_queue,
                correlation_id = self.corr_id,
                content_type = 'application/json'
                ),
            body=data_json
        )
        while self.response is None:
            self.connection.process_data_events()
        print("Got {}".format(self.response))
        return self.response
