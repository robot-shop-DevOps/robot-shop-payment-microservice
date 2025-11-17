import requests
import json

class UserService:
    def __init__(self, host, port, logger):
        self.host = host
        self.port = port
        self.logger = logger

    def check_connection(self):
        try:
            resp = requests.get(f"http://{self.host}:{self.port}/health")
            if resp.status_code != 200:
                return "User microservice not ready", 503
        except Exception as e:
            return e, 503

    def user_exists(self, user_id):
        try:
            resp = requests.get(f"http://{self.host}:{self.port}/check/{user_id}")
            return resp.status_code == 200
        except requests.exceptions.RequestException as e:
            self.logger.error(e)
            return False

    def record_order(self, user_id, order):
        try:
            data = json.dumps({"orderid": order.id, "cart": order.cart})
            resp = requests.post(
                f"http://{self.host}:{self.port}/order/{user_id}",
                data=data,
                headers={"Content-Type": "application/json"}
            )
            self.logger.info(f"Order history returned {resp.status_code}")
        except requests.exceptions.RequestException as e:
            self.logger.error(e)