import pytest
from unittest.mock import MagicMock, patch

from payment.services.payment import PaymentService

@pytest.fixture
def setup_services():
    user_service = MagicMock()
    cart_service = MagicMock()
    queue_service = MagicMock()
    logger = MagicMock()

    payment_service = PaymentService(
        user_service=user_service,
        cart_service=cart_service,
        queue_service=queue_service,
        gateway_url="https://fake-gateway.test",
        logger=logger
    )

    return payment_service, user_service, cart_service, queue_service, logger


def test_payment_service_happy_path(setup_services):
    payment_service, user_service, cart_service, queue_service, logger = setup_services

    # Mock: user exists
    user_service.user_exists.return_value = True

    # Mock cart
    cart = {
        "items": [{"sku": "SHIP", "qty": 1}, {"sku": "ITEM1", "qty": 2}],
        "total": 150
    }

    # Mock payment gateway (HTTP 200)
    with patch("payment.services.payment.requests.get") as mock_get:
        mock_get.return_value.status_code = 200

        order_id = payment_service.process_payment("user123", cart)

        # Validate order ID generated
        assert isinstance(order_id, str)
        assert len(order_id) > 10

        # user history updated
        user_service.record_order.assert_called_once()

        # queue service called
        queue_service.publish_order.assert_called_once()

        # cart service delete called
        cart_service.delete_cart.assert_called_once_with("user123")


def test_payment_service_invalid_cart(setup_services):
    payment_service, user_service, _, _, _ = setup_services

    # Mock user exists
    user_service.user_exists.return_value = True

    invalid_cart = {
        "items": [{"sku": "ITEM1", "qty": 1}],  # No SHIP
        "total": 0
    }

    with pytest.raises(ValueError):
        payment_service.process_payment("u1", invalid_cart)


def test_payment_service_gateway_failure(setup_services):
    payment_service, user_service, _, _, _ = setup_services

    user_service.user_exists.return_value = True

    cart = {
        "items": [{"sku": "SHIP", "qty": 1}],
        "total": 100
    }

    with patch("payment.services.payment.requests.get") as mock_get:
        mock_get.return_value.status_code = 500

        with pytest.raises(Exception):
            payment_service.process_payment("u1", cart)
