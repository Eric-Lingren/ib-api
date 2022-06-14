import ta
import numpy as np
import pandas as pd


class SMA:

    def get_sma_list(period:int, data:list):
        pd_array = pd.Series(np.asarray(data))
        sma_list = ta.trend.sma_indicator(pd_array, period, True)
        return sma_list

    def get_latest_sma(period:int, data:list):
        pd_array = pd.Series(np.asarray(data))
        sma_list = ta.trend.sma_indicator(pd_array, period, True)
        sma = sma_list[len(sma_list)-1]
        return sma