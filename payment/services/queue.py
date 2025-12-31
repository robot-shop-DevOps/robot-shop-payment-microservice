import os
import time

class QueueService:
    def __init__(self, publisher, logger):
        self.logger = logger
        self.publisher = publisher

    def publish_order(self, order):
        self.logger.info("Queueing order")
        delay = 0
        time.sleep(delay / 1000)
        headers = {}
        self.publisher.publish({"orderid": order.id, "user": order.user_id, "cart": order.cart}, headers)