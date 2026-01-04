import pytest
from unittest.mock import MagicMock

from payment.services.queue import QueueService

class FakeOrder:
    def __init__(self):
        self.id = "order123"
        self.user_id = "user123"
        self.cart = {"items": [], "total": 0}

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

    # message published
    assert len(fake_publisher.published_messages) == 1

    msg, headers = fake_publisher.published_messages[0]
    assert msg["orderid"] == "order123"
    assert msg["user"] == "user123"
    assert msg["cart"] == {"items": [], "total": 0}

    # logging happened (but don't over-constrain it)
    fake_logger.info.assert_called()
    args, kwargs = fake_logger.info.call_args
    assert "Queueing order" in args[0]