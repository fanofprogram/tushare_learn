#!/usr/bin/env python3
# -*- coding=utf-8 -*-

__author__ = 'skyeagle'

import datetime

class Tools():
    def __init__(self):
        pass

    @staticmethod
    def getday(dayNum,today=datetime.datetime.today()):
        delta = datetime.timedelta(days=-dayNum)
        d = today - delta
        return d
