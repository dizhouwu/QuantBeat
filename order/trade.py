from order import MarketOrder, LimitOrder, CancelOrder
import pandas as pd


class Trade:
    def __init__(self, side, price, size, order_id, book_order_id):
        self.timestamp = pd.Timestamp.now()
        self.size = size
        self.side = side
        self.order_id = order_id
        self.book_order_id = book_order_id

    def __repr__(self):
        return f"Executed: {self.side} {self.size} units at {self.price}"
