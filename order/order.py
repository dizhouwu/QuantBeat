from enum import Enum

class Side(Enum):
    BUY=0
    SELL=1

class Order:
    def __init__(self, order_id):
        self.order_id = order_id


class CancelOrder:
    def __init__(self, order_id):
        super().__init__(order_id)

class MarketOrder(Order):
    def __init__(self, order_id, side, size):
        super().__init__(order_id)
        self.side = side
        self.size = size

class LimitOrder(Order):
    def __init__(self, order_id, side, size, price):
        super().__init__(order_id)
        self.side = side
        self.price = price

    
