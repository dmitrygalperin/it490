#!/usr/bin/env python
import sys
sys.path.insert(0, "/home/produ/it490/lib")

import pika
from config import RabbitMQ
import logging
import json
from json import JSONDecodeError
from common import unserialize
import reprlib

logging.basicConfig(filename='/var/log/it490/rpc/rpc_sub.log',level=logging.INFO, format='%(asctime)s %(message)s')


class RpcSub(object):

    '''
    RabbitMQ RPC Subscriber
    '''

    def __init__(self, queue, fill_request):
        self.username      = RabbitMQ.username
        self.password      = RabbitMQ.password
        self.host          = RabbitMQ.host
        self.port          = RabbitMQ.port
        self.virtual_host  = RabbitMQ.virtual_host
        self.exchange      = RabbitMQ.exchange
        self.queue         = queue
        self.fill_request  = fill_request

        self.logger = logging.getLogger('rpc_sub')
        self.logger.addHandler(logging.StreamHandler())

    def get_connection(self):
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            return pika.BlockingConnection(pika.ConnectionParameters(self.host, self.port, self.virtual_host, credentials))
        except Exception as e:
            self.logger.critical(e)

    def get_channel(self):
        connection = self.get_connection()
        if connection:
            channel = connection.channel()
            channel.queue_declare(queue=self.queue)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(self.on_request, queue=self.queue)
            return channel
        else:
            return

    def listen(self):
        channel = self.get_channel()
        if channel:
            self.logger.info('Awaiting requests on {}:{}{}{}'.format(self.host, self.port, self.virtual_host, self.queue))
            channel.start_consuming()

    def on_request(self, ch, method, props, body):
        try:
            request = json.loads(body.decode('utf-8'))
            response = self.fill_request(request)
        except JSONDecodeError as e:
            response = {'error': '{}: {}'.format(type(e).__name__, str(e))}
        ch.basic_publish(
            exchange=self.exchange,
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id = props.correlation_id),
            body=json.dumps(response)
        )
        #for obj in [request, response]:
        #    for key, value in obj.items():
        #        try:
        #            obj[key] = unserialize(value)
        #        except:
        #            pass
        self.logger.info('\t\tReceived: {}\n\t\tReturned: {}'.format(reprlib.repr(request), reprlib.repr(response)))
        ch.basic_ack(delivery_tag = method.delivery_tag)
