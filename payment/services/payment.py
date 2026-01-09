import requests
from payment.utils.orders import Order

class PaymentService:
    def __init__(self, user_service, cart_service, queue_service, gateway_url, logger):
        self.user_service  = user_service
        self.cart_service  = cart_service
        self.queue_service = queue_service
        self.gateway_url   = gateway_url
        self.logger        = logger

    def _is_cart_valid(self, cart):
        has_shipping = any(i.get("sku") == "SHIP" for i in cart.get("items", []))
        total        = cart.get("total", 0)
        return has_shipping and total > 0

    def process_payment(self, user_id, cart):
        anonymous_user = not self.user_service.user_exists(user_id)

        if not self._is_cart_valid(cart):
            self.logger.warning(
                "invalid cart",
                extra={
                    "service": "payment",
                    "error_type": "INVALID_CART",
                    "user_id": user_id,
                },
            )
            raise ValueError("Invalid cart")

        try:
            resp = requests.get(self.gateway_url, timeout=3)

        except requests.exceptions.RequestException as e:
            self.logger.error(
                "payment gateway unreachable", 
                str(e),
                extra={
                    "service": "payment",
                    "dependency": "payment_gateway",
                    "error_type": "DEPENDENCY_DOWN",
                    "user_id": user_id,
                    "exception": e.__class__.__name__
                },
            )
            raise Exception("Payment gateway error")

        if resp.status_code != 200:
            self.logger.error(
                "payment gateway returned non-200",
                extra={
                    "service": "payment",
                    "dependency": "payment_gateway",
                    "error_type": "GATEWAY_ERROR",
                    "user_id": user_id,
                    "status_code": resp.status_code,
                },
            )
            raise Exception("Payment gateway error")

        order = Order(user_id, cart)

        try:
            self.queue_service.publish_order(order)
        except Exception as e:
            self.logger.error(
                "failed to publish order",
                extra={
                    "service": "payment",
                    "dependency": "rabbitmq",
                    "error_type": "QUEUE_PUBLISH_FAILED",
                    "user_id": user_id,
                    "order_id": order.id,
                    "exception": e.__class__.__name__,
                },
            )
            raise

        if not anonymous_user:
            try:
                self.user_service.record_order(user_id, order)
            except Exception as e:
                self.logger.error(
                    "failed to record user order",
                    extra={
                        "service": "payment",
                        "dependency": "user",
                        "error_type": "USER_UPDATE_FAILED",
                        "user_id": user_id,
                        "order_id": order.id,
                        "exception": e.__class__.__name__,
                    },
                )
                raise

        self.cart_service.delete_cart(user_id)

        return order.id