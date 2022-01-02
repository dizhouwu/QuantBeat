from order_research.orderbook import OrderBook
from order_research.order import LimitOrder, Side
from time import time
from random import getrandbits, randint, random

ob = OrderBook()
n_orders = 10000
orders = []
for n in range(n_orders):
    if getrandbits(1):
        orders.append(LimitOrder(n, Side.BUY, randint(1, 200), randint(1, 4)))
    else:
        orders.append(LimitOrder(n, Side.SELL, randint(1, 200), randint(1, 4)))


start = time()
for order in orders:
    ob.process_order(order)
end = time()
elapsed = end - start
print(f"Time: {elapsed}")
print(f"Orders per second: {n_orders / elapsed}")
