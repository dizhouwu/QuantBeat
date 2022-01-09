from quant_research.order_research.order import MarketOrder, LimitOrder, CancelOrder, Order
from sortedcontainers import SortedList
from functools import singledispatchmethod
from quant_research.order_research.order import Side
from quant_research.order_research.trade import Trade
from typing import Union


class OrderBook:
    __slots__ = "bids", "asks", "trades"

    def __init__(self):
        self.bids: SortedList[Order] = SortedList()
        self.asks: SortedList[Order] = SortedList()
        self.trades = []

    @singledispatchmethod
    def process_order(self, order):
        raise NotImplementedError

    @process_order.register
    def _(self, order: MarketOrder):
        self._process_order(order)

        if order.remaining > 0:
            if order.side == Side.BUY:
                self.bids.add(order)
            else:
                self.asks.add(order)

    @process_order.register
    def _(self, order: LimitOrder):
        self._process_order(order)
        if order.remaining > 0:
            if order.side == Side.BUY:
                self.bids.add(order)
            else:
                self.asks.add(order)

    def _get_condition(self, order: Union[MarketOrder, LimitOrder]):
        if isinstance(order, LimitOrder):
            if order.side == Side.BUY:
                condition = len(self.asks) > 0 and order.price >= self.asks[0].price
            else:
                condition = len(self.bids) > 0 and order.price <= self.bids[0].price
        else:
            if order.side == Side.BUY:
                condition = len(self.asks) > 0
            else:
                condition = len(self.bids) > 0

        return condition

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
        while self._get_condition(order):
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
                order.remaining = 0

                self.trades.append(
                    Trade(
                        order.side,
                        book_order.price,
                        order.size,
                        order.order_id,
                        book_order.order_id,
                    )
                )

                if order.side == Side.SELL:
                    self.asks.add(order)
                else:
                    self.bids.add(order)

    def get_best_bid(self):
        if len(self.bids):
            return self.bids[0]
        return 0

    def get_best_ask(self):
        if len(self.asks):
            return self.asks[0]
        return 0

    def __repr__(self):
        lines = []
        lines.append("-" * 5 + "OrderBook" + "-" * 5)

        lines.append("\nAsks:")
        asks = self.asks.copy()
        while len(asks) > 0:
            lines.append(str(asks.pop()))

        lines.append("\t" * 3 + "Bids:")
        bids = list(reversed(self.bids.copy()))
        while len(bids) > 0:
            lines.append("\t" * 3 + str(bids.pop()))

        lines.append("-" * 20)
        return "\n".join(lines)

    def __len__(self):
        return len(self.asks) + len(self.bids)
