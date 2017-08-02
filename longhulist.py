#!/usr/bin/env python3
# -*- coding=utf-8 -*-

__author__ = 'skyeagle'

import pandas as pd
import tushare as ts
import datetime
import tools as tls


def top_list(day=datetime.date.today()):
    strday = day.__str__()
    topList = ts.top_list(strday)
    return topList


def continueInTopList(dayNumbers):
    # 获取向前推算n天的日期
    daylist = tls.generateDaysList(dayNumbers)
    longhulist = []
    longhuday = []
    # 获取每天的龙虎榜，并剔除休市的日期
    for day in daylist:
        longhu = top_list(day)
        if longhu is not None:
            longhulist.append(longhu)
            longhuday.append(day)
    # 获取所有上龙虎榜的股票代码
    codelist = []
    for lh in longhulist:
        for i in range(0, len(lh)):
            codelist.append(lh.iloc[i, 0])
    # 统计股票代码出现的次数
    cls = pd.Series(codelist)
    codecount = cls.value_counts()
    interestingCodeList = []
    for i in range(0, len(codecount)):
        counts = codecount.iloc[i]
        if counts >= len(longhuday):
            interestingCodeList.append(codecount.index[i])
    pdlist = pd.DataFrame()
    for code in interestingCodeList:
        for lh in longhulist:
            pdx = lh[lh.loc[:, 'code'] == code]
            if not pdx.empty:
                pdlist = pd.concat([pdlist, pdx], axis=0, join='outer')
    return pdlist


if __name__ == '__main__':
    day = tls.getday(-1)
    # top_list(day)
    longhupdf = continueInTopList(3)
    longhupdf.to_excel("longhu.xlsx")
