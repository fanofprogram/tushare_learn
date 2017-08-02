#!/usr/bin/env python3
# -*- coding=utf-8 -*-

__author__ = 'skyeagle'

import datetime
import pandas as pd

def getday(dayNum=0, today=datetime.date.today()):
    delta = datetime.timedelta(days=-dayNum)
    d = today - delta
    return d

def generateDaysList(daynumbers):
    startDay = getday(-daynumbers)
    dayIndex = pd.date_range(startDay, periods=daynumbers + 1)
    daylist = []
    for day in dayIndex:
        d = day.__str__().split(' ')[0]
        daylist.append(d)
    return daylist
