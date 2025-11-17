import requests
import time
import os
from payment.utils.orders import Order

class PaymentService:
    def __init__(self, user_service, cart_service, queue_service, gateway_url, logger):
        self.user_service = user_service
        self.cart_service = cart_service
        self.queue_service = queue_service
        self.gateway_url = gateway_url
        self.logger = logger

    def _is_cart_valid(self, cart):
        has_shipping = any(i.get('sku') == 'SHIP' for i in cart.get('items', []))
        total = cart.get('total', 0)
        return has_shipping and total > 0

    def process_payment(self, user_id, cart):
        self.logger.info(f"Payment for {user_id}")
        self.logger.info(cart)

        # Check user
        anonymous_user = not self.user_service.user_exists(user_id)

        # Validate cart
        if not self._is_cart_valid(cart):
            self.logger.warning("Cart not valid")
            raise ValueError("Invalid cart")

        # Simulate payment gateway call
        try:
            req = requests.get(self.gateway_url)
            self.logger.info(f"{self.gateway_url} returned {req.status_code}")
        except requests.exceptions.RequestException as e:
            self.logger.error(e)
            raise Exception("Payment gateway error")
        if req.status_code != 200:
            raise Exception(f"Payment gateway returned {req.status_code}")

        # Create order object
        order = Order(user_id, cart)

        # Queue order for processing
        self.queue_service.publish_order(order)

        # Add to user history if not anonymous
        if not anonymous_user:
            self.user_service.record_order(user_id, order)

        # Delete cart
        self.cart_service.delete_cart(user_id)

        return order.id