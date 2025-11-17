from flask import Flask, Response
import os
import logging

from routes.payment import init_routes
from services.payment import PaymentService
from services.user import UserService
from services.cart import CartService
from services.queue import QueueService
from rabbitmq.rabbitmq import Publisher
from utils.logger import Logger

app = Flask(__name__)
app.logger = Logger().create_logger()

CART = os.getenv('CART_HOST')
CART_PORT = os.getenv('CART_PORT')
USER = os.getenv('USER_HOST')
USER_PORT = os.getenv('USER_PORT')
AMQP_HOST = os.getenv('AMQP_HOST')
AMQP_USER = os.getenv('AMQP_USER')
AMQP_PASS = os.getenv('AMQP_PASS')
PAYMENT_GATEWAY = 'https://paypal.com/'

user_service = UserService(USER, USER_PORT, app.logger)
cart_service = CartService(CART, CART_PORT, app.logger)
publisher    = Publisher(AMQP_HOST, AMQP_USER, AMQP_PASS, app.logger)
queue_service = QueueService(publisher, app.logger)
payment_service = PaymentService(user_service, cart_service, queue_service, PAYMENT_GATEWAY, app.logger)

app.register_blueprint(init_routes(payment_service))

@app.route('/health')
def health():
    msg, status = user_service.check_connection()
    if status != 200:
        return msg, status

    msg, status = cart_service.check_connection()
    if status != 200:
        return msg, status

    msg, status = publisher.check_connection()
    if not status:
        return msg, 503

    return "OK", 200

if __name__ == "__main__":
    port = int(os.getenv("PAYMENT_SERVER_PORT"))
    app.logger.info(f"Payment gateway: {PAYMENT_GATEWAY}")
    app.logger.info(f"Starting on port {port}")
    app.run(host="0.0.0.0", port=port)