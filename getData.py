#!/usr/bin/env python3
# -*- coding=utf-8 -*-

__author__ = 'skyeagle'

import time, datetime
import tushare as ts


def getday(today, dayNum):
    delta = datetime.timedelta(days=-dayNum)
    d = today - delta
    return d


def industry_classified():
    ic = ts.get_industry_classified()
    print(ic)


# 对某只股票的大单进行分析
def dadan(code, day, volume):
    """
    :param code: 股票代码
    :param day: 日期
    :param volume: 交易股票数量
    :return:
    """

    dd = ts.get_sina_dd(code, day, volume)
    buy = dd[dd['type'].isin(['买盘'])]
    sell = dd[dd['type'].isin(['卖盘'])]
    buy_col = buy['volume'].values
    sell_col = sell['volume'].values
    print(buy_col)
    print(sum(buy_col))
    print(sell_col)
    print(sum(sell_col))


if __name__ == "__main__":
    today = datetime.date.today()
    dateDay = getday(today, 0)
    dadan(dateDay)
