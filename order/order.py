from enum import Enum


class Side(Enum):
    BUY = 0
    SELL = 1


class Order:
    def __init__(self, order_id):
        self.order_id = order_id


class CancelOrder(Order):
    __slots__ = "order_id"

    def __init__(self, order_id):
        super().__init__(order_id)


class MarketOrder(Order):
    __slots__ = "order_id", "side", "size"

    def __init__(self, order_id, side, size):
        super().__init__(order_id)

        self.side = side
        self.size = size
        self.remaining = size


class LimitOrder(Order):
    __slots__ = "order_id", "side", "size", "price"

    def __init__(self, order_id, side, size, price):
        super().__init__(order_id)
        self.side = side
        self.price = price
        self.size = size

    def __lt__(self, other):
        if self.price != other.price:
            if self.side == Side.BUY:
                return self.price > other.price
            else:
                return self.price < other.price
        elif self.time != other.time:
            return self.time < other.time

        elif self.size != other.size:
            self.size < other.size
