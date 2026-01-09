from flask import Flask, Response
import os
import sys
import traceback

from payment.routes.payment import init_routes
from payment.services.payment import PaymentService
from payment.services.user import UserService
from payment.services.cart import CartService
from payment.services.queue import QueueService
from payment.rabbitmq.rabbitmq import Publisher
from payment.utils.logger import get_logger

# -------------------------
# App & Logger
# -------------------------
app = Flask(__name__)
logger = get_logger("payment")

# Disable Flask’s default logger noise
app.logger.handlers = []
app.logger.propagate = False

# -------------------------
# Config
# -------------------------
CART            = os.getenv("CART_HOST")
CART_PORT       = os.getenv("CART_PORT")
USER            = os.getenv("USER_HOST")
USER_PORT       = os.getenv("USER_PORT")
AMQP_HOST       = os.getenv("AMQP_HOST")
AMQP_USER       = os.getenv("AMQP_USER")
AMQP_PASS       = os.getenv("AMQP_PASS")
PAYMENT_GATEWAY = "https://paypal.com/"

# -------------------------
# Services
# -------------------------
user_service    = UserService(USER, USER_PORT, logger)
cart_service    = CartService(CART, CART_PORT, logger)
publisher       = Publisher(AMQP_HOST, AMQP_USER, AMQP_PASS, logger)
queue_service   = QueueService(publisher, logger)
payment_service = PaymentService(
    user_service,
    cart_service,
    queue_service,
    PAYMENT_GATEWAY,
    logger,
)

app.register_blueprint(init_routes(payment_service))

# -------------------------
# Health
# -------------------------
@app.route("/health")
def health():
    msg, status = user_service.check_connection()
    if status != 200:
        logger.warning(
            "user service unhealthy",
            extra={
                "dependency": "user",
                "error_type": "DEPENDENCY_UNHEALTHY",
            },
        )
        return msg, status

    msg, status = cart_service.check_connection()
    if status != 200:
        logger.warning(
            "cart service unhealthy",
            extra={
                "dependency": "cart",
                "error_type": "DEPENDENCY_UNHEALTHY",
            },
        )
        return msg, status

    ok = publisher.check_connection()
    if not ok:
        logger.error(
            "rabbitmq unavailable",
            extra={
                "dependency": "rabbitmq",
                "error_type": "DEPENDENCY_DOWN",
            },
        )
        return "RabbitMQ unavailable", 503

    return "OK", 200

# -------------------------
# Global exception handler
# -------------------------
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(
        "unhandled application exception",
        extra={
            "error_type": "UNHANDLED_EXCEPTION",
            "exception": e.__class__.__name__
        },
    )
    return Response("Internal Server Error", status=500)

# -------------------------
# Startup
# -------------------------
if __name__ == "__main__":
    port = int(os.getenv("PAYMENT_SERVER_PORT", "8080"))

    logger.info(
        "payment service starting",
        extra={
            "service": "payment",
            "port": port,
        },
    )

    app.run(host="0.0.0.0", port=port)