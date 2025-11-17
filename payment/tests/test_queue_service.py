import pytest
from unittest.mock import MagicMock

from payment.services.queue import QueueService

# Fake order object for testing
class FakeOrder:
    def __init__(self):
        self.id = "order123"
        self.user_id = "user123"
        self.cart = {"items": [], "total": 0}

# Fake publisher that records messages instead of sending to real RabbitMQ
class FakePublisher:
    def __init__(self):
        self.published_messages = []

    def publish(self, message, headers):
        self.published_messages.append((message, headers))

def test_queue_service_publishes_order():
    fake_publisher = FakePublisher()
    fake_logger = MagicMock()

    service = QueueService(fake_publisher, fake_logger)
    order = FakeOrder()

    service.publish_order(order)

    assert len(fake_publisher.published_messages) == 1

    msg, headers = fake_publisher.published_messages[0]

    assert msg["orderid"] == "order123"
    assert msg["user"] == "user123"
    assert msg["cart"] == {"items": [], "total": 0}

    fake_logger.info.assert_called_with("Queueing order")
