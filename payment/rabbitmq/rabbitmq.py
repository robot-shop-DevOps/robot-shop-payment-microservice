import json
import pika
import os

class Publisher:
    def __init__(self, host, user, password, logger):
        self.HOST = host
        self.USER = user
        self.password = password
        self.VIRTUAL_HOST = '/'
        self.EXCHANGE='robot-shop'
        self.TYPE='direct'
        self.ROUTING_KEY = 'orders'
        self._logger = logger
        self._params = pika.connection.ConnectionParameters(
            host=self.HOST,
            virtual_host=self.VIRTUAL_HOST,
            credentials=pika.credentials.PlainCredentials(self.USER, self.password))
        self._conn = None
        self._channel = None

    def _connect(self):
        if not self._conn or self._conn.is_closed or self._channel is None or self._channel.is_closed:
            self._conn = pika.BlockingConnection(self._params)
            self._channel = self._conn.channel()
            self._channel.exchange_declare(exchange=self.EXCHANGE, exchange_type=self.TYPE, durable=True)
            self._logger.info('connected to broker')

    def _publish(self, msg, headers):
        self._channel.basic_publish(exchange=self.EXCHANGE,
                                    routing_key=self.ROUTING_KEY,
                                    properties=pika.BasicProperties(headers=headers),
                                    body=json.dumps(msg).encode())
        self._logger.info('message sent')

    def check_connection(self):
        try:
            conn = pika.BlockingConnection(self._params)
            conn.close()
            return "OK", True
        except Exception as e:
            return f"RabbitMQ unreachable: {e}", False
            
    #Publish msg, reconnecting if necessary.
    def publish(self, msg, headers):
        if self._channel is None or self._channel.is_closed or self._conn is None or self._conn.is_closed:
            self._connect()
        try:
            self._publish(msg, headers)
        except (pika.exceptions.ConnectionClosed, pika.exceptions.StreamLostError):
            self._logger.info('reconnecting to queue')
            self._connect()
            self._publish(msg, headers)

    def close(self):
        if self._conn and self._conn.is_open:
            self._logger.info('closing queue connection')
            self._conn.close()