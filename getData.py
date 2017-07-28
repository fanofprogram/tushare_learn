#!/usr/bin/env python3
# -*- coding=utf-8 -*-

__author__ = 'skyeagle'

import time, datetime
import tushare as ts


def getday(dayNum):
    today = datetime.date.today()
    delta = datetime.timedelta(days=-dayNum)
    d = today - delta
    return d


def industry_classified():
    ic = ts.get_industry_classified()
    print(ic)


def dadan(day):
    dd = ts.get_sina_dd('600755', day, vol=1000)
    buy=dd[dd['type'].isin(['买盘'])]
    sell=dd[dd['type'].isin(['卖盘'])]
    print(buy['volume'])



if __name__ == "__main__":
    today = time.strftime("%y-%m-%d")
    dateDay=getday(0)
    dadan(dateDay)
