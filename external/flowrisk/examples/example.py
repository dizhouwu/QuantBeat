from toxicity.vpin import BulkConfVPINConfig
from examples.usstocks import USStocks


class Config(BulkConfVPINConfig):
    N_TIME_BAR_FOR_INITIALIZATION = 50


config = Config()

example = USStocks(config)
symbols = example.list_symbols("small")
result = example.estimate_vpin_and_conf_interval(symbols[0])

if __name__ == "__main__":
    example.draw_price_vpins_and_conf_intervals()
