from quant_research.order_research.order import Side
from time import time


class Trade:
    __slots__ = (
        "ts",
        "size",
        "side",
        "price",
        "order_id",
        "book_order_id",
    )

    def __init__(
        self, size: int, side: Side, price: float, order_id: int, book_order_id: int
    ):
        self.ts = int(1e6 * time())
        self.size = size
        self.side = side
        self.price = price
        self.order_id = order_id
        self.book_order_id = book_order_id

    def __repr__(self):
        return f"Executed: {self.side} {self.size} units at {self.price}"
