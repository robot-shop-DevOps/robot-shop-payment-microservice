class QueueService:
    def __init__(self, publisher, logger):
        self.publisher = publisher
        self.logger    = logger

    def publish_order(self, order):

        self.logger.info(
            "Queueing order",
            extra={
                "orderid": order.id,
                "user": order.user_id
            }
        )

        try:
            self.publisher.publish(
                {
                    "orderid": order.id,
                    "user": order.user_id,
                    "cart": order.cart,
                },
                headers={},
            )

        except Exception as e:
            self.logger.error(
                "failed to publish order to queue",
                extra={
                    "dependency": "rabbitmq",
                    "error_type": "QUEUE_PUBLISH_FAILED",
                    "order_id": order.id,
                    "exception": e.__class__.__name__,
                    "message": str(e),
                },
            )
            raise