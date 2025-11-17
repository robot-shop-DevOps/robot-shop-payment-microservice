from flask import Blueprint, request, jsonify

bp = Blueprint("payment", __name__)

def init_routes(payment_service):
    @bp.route('/pay/<user_id>', methods=['POST'])
    def pay(user_id):
        try:
            cart = request.get_json()
            order_id = payment_service.process_payment(user_id, cart)
            return jsonify({"orderid": order_id})
        except ValueError as e:
            return str(e), 400
        except Exception as e:
            payment_service.logger.error(str(e))
            return str(e), 500

    return bp