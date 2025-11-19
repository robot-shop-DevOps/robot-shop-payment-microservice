import requests

class CartService:
    def __init__(self, host, port, logger):
        self.host = host
        self.port = port
        self.logger = logger

    def check_connection(self):
        try:
            resp = requests.get(f"http://{self.host}:{self.port}/health")
            if resp.status_code != 200:
                return "Cart microservice not ready", 503
        except Exception as e:
            return e, 503
        
        return "OK", 200

    def delete_cart(self, user_id):
        try:
            resp = requests.delete(f"http://{self.host}:{self.port}/cart/{user_id}")
            self.logger.info(f"Cart delete returned {resp.status_code}")
            if resp.status_code != 200:
                raise Exception("Cart deletion failed")
        except requests.exceptions.RequestException as e:
            self.logger.error(e)
            raise