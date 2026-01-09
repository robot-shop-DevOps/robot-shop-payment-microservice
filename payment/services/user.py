import requests
import json


class UserService:
    def __init__(self, host, port, logger):
        self.host   = host
        self.port   = port
        self.logger = logger

    def check_connection(self):
        try:
            resp = requests.get(
                f"http://{self.host}:{self.port}/health",
                timeout=3,
            )

            if resp.status_code != 200:
                self.logger.warning(
                    "user service unhealthy",
                    extra={
                        "dependency": "user",
                        "error_type": "DEPENDENCY_UNHEALTHY",
                        "status_code": resp.status_code,
                    },
                )
                return "User microservice not ready", 503

        except requests.exceptions.RequestException as e:
            self.logger.error(
                "user service unreachable",
                extra={
                    "dependency": "user",
                    "error_type": "DEPENDENCY_DOWN",
                    "exception": e.__class__.__name__
                },
            )
            return "User microservice unreachable", 503

        return "OK", 200

    def user_exists(self, user_id):
        try:
            resp = requests.get(
                f"http://{self.host}:{self.port}/check/{user_id}",
                timeout=3,
            )
            return resp.status_code == 200

        except requests.exceptions.RequestException as e:
            self.logger.error(
                "user service error during lookup",
                extra={
                    "dependency": "user",
                    "error_type": "DEPENDENCY_DOWN",
                    "user_id": user_id,
                    "exception": e.__class__.__name__,
                },
            )
            return False

    def record_order(self, user_id, order):
        try:
            resp = requests.post(
                f"http://{self.host}:{self.port}/order/{user_id}",
                data=json.dumps({"orderid": order.id, "cart": order.cart}),
                headers={"Content-Type": "application/json"},
                timeout=3,
            )

            if resp.status_code != 200:
                self.logger.error(
                    "failed to record user order",
                    extra={
                        "dependency": "user",
                        "error_type": "ORDER_RECORD_FAILED",
                        "user_id": user_id,
                        "order_id": order.id,
                        "status_code": resp.status_code,
                    },
                )
                raise Exception("User order record failed")

        except requests.exceptions.RequestException as e:
            self.logger.error(
                "user service error during order record",
                extra={
                    "dependency": "user",
                    "error_type": "DEPENDENCY_DOWN",
                    "user_id": user_id,
                    "order_id": order.id,
                    "exception": e.__class__.__name__
                },
            )
            raise