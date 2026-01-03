from flask import Blueprint, request, jsonify

bp = Blueprint("payment", __name__)

def init_routes(payment_service):
    logger = payment_service.logger

    @bp.route("/pay/<user_id>", methods=["POST"])
    def pay(user_id):
        try:
            cart = request.get_json()
            order_id = payment_service.process_payment(user_id, cart)

            return jsonify({"orderid": order_id})

        except ValueError as e:
            logger.warning(
                "payment validation failed",
                extra={
                    "service": "payment",
                    "error_type": "INVALID_PAYMENT_REQUEST",
                    "user_id": user_id,
                    "message": str(e),
                },
            )

            return str(e), 400

        except Exception as e:
            logger.error(
                "payment processing failed",
                extra={
                    "service": "payment",
                    "error_type": "PAYMENT_FAILED",
                    "user_id": user_id,
                    "exception": e.__class__.__name__,
                    "message": str(e),
                },
            )

            return "Payment failed", 500

    return bp