from order import MarketOrder, LimitOrder, CancelOrder
from sortedcontainers import SortedList
from functools import singledispatchmethod


class OrderBook:
    def __init__(self):
        self.bids = SortedList()
        self.asks = SortedList()
        self.trades = []

    @singledispatchmethod
    def process_order(self, order):
        raise NotImplementedError

    @process_order.register
    def _(self, order: MarketOrder):
        ...

    @process_order.regester
    def _(self, order: LimitOrder):
        ...

    @process_order.regester
    def _(self, order: CancelOrder):
        for bid in self.bids:
            if bid.id == order.id:
                self.bids.discard(order)
                return
        for ask in self.asks:
            if ask.id == order.id:
                self.asks.discard(order)
                return
