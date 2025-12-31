import uuid

class Order:
    def __init__(self, user_id, cart):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.cart = cart

    def item_count(self):
        return sum(
            item.get('qty', 0)
            for item in self.cart.get('items', [])
            if item.get('sku') != 'SHIP'
        )

    def total_value(self):
        return self.cart.get('total', 0)