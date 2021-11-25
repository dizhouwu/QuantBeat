from enum import Enum
from time import time


class Side(Enum):
    BUY = 0
    SELL = 1


class Order:
    __slots__ = "order_id", "ts"

    def __init__(self, order_id):
        self.order_id = order_id
        self.ts = int(1e6 * time())


class CancelOrder(Order):
    __slots__ = "order_id", "ts"

    def __init__(self, order_id):
        super().__init__(order_id)


class MarketOrder(Order):
    __slots__ = "order_id", "side", "size", "remaining", "ts"

    def __init__(self, order_id, side, size):
        super().__init__(order_id)
        self.side = side
        self.size = size
        self.remaining = size

    def __repr__(self):
        return f"Market Order {self.side} {self.size} {self.ts}"


class LimitOrder(Order):
    __slots__ = "order_id", "side", "size", "remaining", "price", "ts"

    def __init__(self, order_id, side, size, price):
        super().__init__(order_id)
        self.side = side
        self.price = price
        self.size = size
        self.remaining = size

    def __lt__(self, other):
        if self.price != other.price:
            if self.side == Side.BUY:
                return self.price > other.price
            else:
                return self.price < other.price
        elif self.ts != other.ts:
            return self.ts < other.ts

        elif self.size != other.size:
            return self.size < other.size

    def __repr__(self):
        return f"Limit Order {self.side} {self.size} {self.ts}"
