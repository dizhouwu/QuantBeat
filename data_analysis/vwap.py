from numba import njit
import pandas as pd
import numpy as np

df = pd.DataFrame(np.random.randn(10000, 3), columns=["v", "h", "l"])

df["vwap_pandas"] = (df.v * (df.h + df.l) / 2).cumsum() / df.v.cumsum()


@njit
def np_vwap():
    return np.cumsum(v * (h + l) / 2) / np.cumsum(v)


v = df.v.values
h = df.h.values
l = df.l.values

df["vwap_numpy"] = np.cumsum(v * (h + l) / 2) / np.cumsum(v)

df["vwap_numba"] = np_vwap()
