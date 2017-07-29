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
        self.day=day
        self.buy = dd[dd['type'].isin(['买盘'])]
        self.sell = dd[dd['type'].isin(['卖盘'])]

    def timePlot(self, dd, timeDelta):
        timeVol = dd.loc[:, ['time', 'volume']]
        timeVol = timeVol.sort_values(by='time')

        self.rearrange(timeVol, timeDelta)
        # plt.show()

    def rearrange(self, dd, timeDelta):
        sTime = '09:30:00'
        eTime = '15:00:00'

        startTime = sTime
        endTime = datetime.datetime(startTime) + datetime.timedelta(minutes=30)
        print(endTime)

        tmp = dd[dd.loc[:, 'time'] < endTime]
        sx = tmp[tmp.loc[:, 'time'] > startTime]
        print(sx)

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
    dateDay = getday(today, -1)
    bd = Bigdeal('600516', dateDay, 1000)
    bd.buyTimePlot(1)
