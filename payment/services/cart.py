import requests


class CartService:
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
                    "cart service unhealthy",
                    extra={
                        "dependency": "cart",
                        "error_type": "DEPENDENCY_UNHEALTHY",
                        "status_code": resp.status_code,
                    },
                )
                return "Cart microservice not ready", 503

        except requests.exceptions.RequestException as e:
            self.logger.error(
                "cart service unreachable",
                extra={
                    "dependency": "cart",
                    "error_type": "DEPENDENCY_DOWN",
                    "exception": e.__class__.__name__,
                    "message": str(e),
                },
            )
            return "Cart microservice unreachable", 503

        return "OK", 200

    def delete_cart(self, user_id):
        try:
            resp = requests.delete(
                f"http://{self.host}:{self.port}/cart/{user_id}",
                timeout=3,
            )

            if resp.status_code != 200:
                self.logger.error(
                    "cart deletion failed",
                    extra={
                        "dependency": "cart",
                        "error_type": "DELETE_FAILED",
                        "user_id": user_id,
                        "status_code": resp.status_code,
                    },
                )
                raise Exception("Cart deletion failed")

        except requests.exceptions.RequestException as e:
            self.logger.error(
                "cart service error during delete",
                extra={
                    "dependency": "cart",
                    "error_type": "DEPENDENCY_DOWN",
                    "user_id": user_id,
                    "exception": e.__class__.__name__,
                    "message": str(e),
                },
            )
            raise