import json
import pika


class Publisher:
    def __init__(self, host, user, password, logger):
        self.HOST          = host
        self.USER          = user
        self.password      = password
        self.VIRTUAL_HOST  = "/"
        self.EXCHANGE      = "robot-shop"
        self.TYPE          = "direct"
        self.ROUTING_KEY   = "orders"

        self._logger  = logger
        self._conn    = None
        self._channel = None

        self._params = pika.ConnectionParameters(
            host=self.HOST,
            virtual_host=self.VIRTUAL_HOST,
            credentials=pika.PlainCredentials(self.USER, self.password),
        )

    def _connect(self):
        try:
            self._conn = pika.BlockingConnection(self._params)
            self._channel = self._conn.channel()
            self._channel.exchange_declare(
                exchange=self.EXCHANGE,
                exchange_type=self.TYPE,
                durable=True,
            )
        except Exception as e:
            self._logger.error(
                "failed to connect to rabbitmq",
                extra={
                    "dependency": "rabbitmq",
                    "error_type": "DEPENDENCY_DOWN",
                    "exception": e.__class__.__name__,
                    "message": str(e),
                },
            )
            raise

    def _publish(self, msg, headers):
        self._channel.basic_publish(
            exchange=self.EXCHANGE,
            routing_key=self.ROUTING_KEY,
            properties=pika.BasicProperties(headers=headers),
            body=json.dumps(msg).encode(),
        )

    def publish(self, msg, headers):
        try:
            if (
                self._conn is None
                or self._conn.is_closed
                or self._channel is None
                or self._channel.is_closed
            ):
                self._connect()

            self._publish(msg, headers)

        except (
            pika.exceptions.ConnectionClosed,
            pika.exceptions.StreamLostError,
            pika.exceptions.AMQPConnectionError,
        ) as e:
            self._logger.warning(
                "rabbitmq connection lost, reconnecting",
                extra={
                    "dependency": "rabbitmq",
                    "error_type": "RECONNECTING",
                    "exception": e.__class__.__name__,
                },
            )

            self._connect()
            self._publish(msg, headers)

        except Exception as e:
            self._logger.error(
                "failed to publish message",
                extra={
                    "dependency": "rabbitmq",
                    "error_type": "PUBLISH_FAILED",
                    "exception": e.__class__.__name__,
                    "message": str(e),
                },
            )
            raise

    def check_connection(self):
        try:
            conn = pika.BlockingConnection(self._params)
            conn.close()
            return "OK", True

        except Exception as e:
            self._logger.error(
                "rabbitmq health check failed",
                extra={
                    "dependency": "rabbitmq",
                    "error_type": "DEPENDENCY_DOWN",
                    "exception": e.__class__.__name__,
                    "message": str(e),
                },
            )
            return "RabbitMQ unreachable", False