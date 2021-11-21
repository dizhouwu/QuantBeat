from order import MarketOrder, LimitOrder, CancelOrder
from sortedcontainers import SortedList
from functools import singledispatchmethod
from order import Side
from trade import Trade
from typing import Union


class OrderBook:
    __slots__ = "bids", "asks", "trades"

    def __init__(self):
        self.bids = SortedList()
        self.asks = SortedList()
        self.trades = []

    @singledispatchmethod
    def process_order(self, order):
        raise NotImplementedError

    @process_order.register
    def _(self, order: MarketOrder):
        self._process_order(order)

    @process_order.register
    def _(self, order: LimitOrder):
        self._process_order(order)
        if order.remaining > 0:
            if order.side == Side.BUY:
                self.bids.add(order)
            else:
                self.asks.add(order)

    @process_order.register
    def _(self, order: CancelOrder):
        for bid in self.bids:
            if bid.id == order.id:
                self.bids.discard(order)
                return
        for ask in self.asks:
            if ask.id == order.id:
                self.asks.discard(order)
                return

    def _process_order(self, order: Union[MarketOrder, LimitOrder]):
        if order.side == Side.BUY:
            condition = len(self.asks) > 0
        else:
            condition = len(self.bids) > 0

        while condition:
            if order.side == Side.BUY:
                book_order = self.asks.pop(0)
            else:
                book_order = self.bids.pop(0)

            if order.remaining >= book_order.remaining:
                order.remaining -= book_order.remaining
                book_order.remaining = 0

                self.trades.append(
                    Trade(
                        order.side,
                        book_order.price,
                        order.size,
                        order.order_id,
                        book_order.order_id,
                    )
                )
                if order.remaining == 0:
                    break
            else:
                order.remaining -= book_order.remaining
                book_order.remaining = 0

                self.trades.append(
                    Trade(
                        order.side,
                        book_order.price,
                        order.size,
                        order.order_id,
                        book_order.order_id,
                    )
                )

                if order.size == Side.SELL:
                    self.asks.add(order)
                else:
                    self.bids.add(order)

    def get_best_bid(self):
        return self.bids[0]

    def get_best_ask(self):
        return self.asks[0]

    def __repr__(self):
        print(f"bids: {self.bids}")
        print(f"asks: {self.asks}")

    def __len__(self):
        return len(self.asks) + len(self.bids)
