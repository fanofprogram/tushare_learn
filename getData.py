#!/usr/bin/env python3
# -*- coding=utf-8 -*-

__author__ = 'skyeagle'

import time, datetime
import tushare as ts
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Bigdeal():
    def __init__(self, code, day, volume):
        dd = ts.get_sina_dd(code, day, volume)
        self.day = day
        self.buy = dd[dd['type'].isin(['买盘'])]
        self.sell = dd[dd['type'].isin(['卖盘'])]

    def timePlot(self, dd, timeDelta):
        timeVol = dd.loc[:, ['time', 'volume']]
        timeVol = timeVol.sort_values(by='time')

        bigdf = self.rearrange(timeVol, timeDelta)
        bigdf.plot(x='time', y='volume', kind='bar')


    def rearrange(self, dd, timeDelta):

        # 生成时间间隔为timeDelta的DatetimeIndex
        # 然后转换为时间的字符串
        sTime = '09:30:00'
        eTime = '15:00:00'
        f = timeDelta.__str__() + 'Min'
        rng = pd.date_range(sTime, eTime, freq=f)
        timeList = []
        for r in rng:
            t = r.time().__str__()
            timeList.append(t)

        # 获取时间间隔内的大单交易量的和，方法为求出所有的和，
        # 然后减去此时间间隔前的所有交易量
        bigDealList = []
        for i in range(0, len(timeList)):
            bdt = dd[dd.loc[:, 'time'] < timeList[i]]
            bdt = bdt.apply(np.cumsum)
            if not bdt.empty:
                x = bdt.iloc[len(bdt) - 1, 1]
                if i != 0:
                    value = x - np.sum(bigDealList[i - 1])
                    bigDealList.append(value)
                else:
                    bigDealList.append(x)
            else:
                bigDealList.append(0)

        bigDF = pd.DataFrame({'time': timeList, 'volume': bigDealList})

        return bigDF

    def buyTimePlot(self, timeDelta=30):
        self.timePlot(self.buy, timeDelta)

    def sellTimePlot(self, timeDelta=30):
        self.timePlot(self.sell, timeDelta)


def getday(today, dayNum):
    delta = datetime.timedelta(days=-dayNum)
    d = today - delta
    return d


if __name__ == "__main__":
    today = datetime.date.today()
    dataDay = getday(today, -2)
    bd = Bigdeal('600516', dataDay, 100)
    plt.figure()
    bd.buyTimePlot()
    bd.sellTimePlot()
