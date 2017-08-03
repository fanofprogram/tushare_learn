#!/usr/bin/env python3
# -*- coding=utf-8 -*-

__author__ = 'skyeagle'

import datetime
import tushare as ts
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager
import tools as tls


class Bigdeal():
    """
    通过ts的get_sina_dd函数获取大单数据，然后进行画图处理分析
    """

    def __init__(self, code, day=datetime.date.today(), volume=500):
        """
        :param code:股票代码
        :param day:日期
        :param volume:股票数量,单位为手
        """
        # isOpen主要用于判断是否休市或停盘
        self.isOpen = True
        dd = ts.get_sina_dd(code, day, volume)
        if dd is None:
            self.isOpen = False
        else:
            self.volume = volume
            self.stockname = dd.iloc[0, 1]
            self.day = day
            # 分别提取买盘和卖盘
            self.buy = dd[dd['type'].isin(['买盘'])]
            self.sell = dd[dd['type'].isin(['卖盘'])]

    def getTotal(self, dd):
        # 获取买盘或卖盘的总钱数
        priceVol = dd.loc[:, ['price', 'volume']]
        money = priceVol.loc[:, 'price'] * priceVol.loc[:, 'volume']
        totalmoney = sum(list(money))
        return totalmoney

    def getTotalBuy(self):
        return self.getTotal(self.buy)

    def getTotalSell(self):
        return self.getTotal(self.sell)

    def getNetBigDeal(self):
        # 净流入或净流出钱数
        return self.getTotalBuy() - self.getTotalSell()

    def oneDayPlot(self, timeDelta=30):
        """
        :param timeDelta: 时间间隔，单位分钟
        :return:
        """
        # 使用fc-list :lang=zh查看系统中的中文字体
        myfont = matplotlib.font_manager.FontProperties(fname="/usr/share/fonts/win10/STZHONGS.TTF")

        # 对买盘或卖盘进行数据处理，主要是将某个时间段内的大单求和
        dd = self.buy
        timeVol = dd.loc[:, ['time', 'volume']]
        timeVol = timeVol.sort_values(by='time')
        bigBuyDF = self.rearrange(timeVol, timeDelta)

        dd = self.sell
        timeVol = dd.loc[:, ['time', 'volume']]
        timeVol = timeVol.sort_values(by='time')
        bigSellDF = self.rearrange(timeVol, timeDelta)

        # 获取固定时间间隔的时间列表
        timelist = []
        for t in list(bigBuyDF.iloc[:, 0]):
            strT = t[:-3]
            timelist.append(strT)

        # 原始获得的大单单位是股，除以100换算为手
        blist = list(bigBuyDF.iloc[:, 1] / 100)
        slist = list(bigSellDF.iloc[:, 1] / 100)

        ax = plt.subplot(111)
        # 生成bar的横坐标，买盘和卖盘的图像紧挨着，宽度都为1，和下一个间隔0.5
        # 所以要乘以2.5
        x = np.arange(0, len(timelist))
        x1 = x * 2.5
        x2 = x1 + 1

        plt.bar(left=x1, height=blist, width=1, color='red')
        plt.hold
        plt.bar(left=x2, height=slist, width=1, color='green')

        # 将横坐标表示为时间
        plt.xticks(x2, timelist)
        plt.legend(['buy', 'sell'], loc='upper center', fancybox=True, shadow=True)
        # 纵坐标单位改为整数
        ax.get_yaxis().set_major_formatter(plt.FormatStrFormatter('%i'))
        # plt.setp(ax.get_xaxis().get_majorticklabels(), rotation=-45)

        yl = u'单位(手）'
        plt.ylabel(yl, fontproperties=myfont)

        title = u"%s在%s日超过%d手的大单交易量分时图" % (self.stockname, self.day, self.volume)
        plt.title(title, fontproperties=myfont)

        #钱数除以10000，单位万元
        money = round(self.getNetBigDeal() / 10000)
        strMoney = u"%s在%s日超过%d手的大单净流入人民币%d万元" % (self.stockname, self.day, self.volume, money)
        if money < 0:
            strMoney = u"%s在%s日超过%d手的大单净流出人民币%d万元" % (self.stockname, self.day, self.volume, money)
        textx = x1[1]
        texty = max([max(slist), max(blist)]) * 7 / 8
        plt.text(6, texty, strMoney, fontproperties=myfont)

        plt.show()

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
            # 剔除11：30-13：00的时间段
            if t == '12:00:00' or t == '12:30:00' or t == '13:00:00':
                continue
            timeList.append(t)
        print(timeList)

        # 获取时间间隔内的大单交易量的和，方法为求出所有的和，
        # 然后减去此时间间隔前的所有交易量
        bigDealList = []
        for i in range(0, len(timeList)):
            if i == 0:
                bdt = dd[dd.loc[:, 'time'] < timeList[i]]
            else:
                bdt = dd[(dd.loc[:, 'time'] < timeList[i]) & (dd.loc[:, 'time'] > timeList[i - 1])]
            # 时间段内求大单的量
            total = sum(list(bdt.loc[:, 'volume']))
            bigDealList.append(total)
        bigDF = pd.DataFrame({'time': timeList, 'volume': bigDealList})

        return bigDF

    @staticmethod
    def numberDaysPlot(code, daysNumbers, volume=500):
        """
         静态方法，获取连续n天的大单数量，并统计分析画图
        :param code:股票代码
        :param daysNumbers:天数，以当前日期往前推
        :param volume:大单
        :return:
        """
        #获取起始日期
        startDay = tls.getday(-daysNumbers)
        dayIndex = pd.date_range(startDay, periods=daysNumbers + 1)
        buylist = []
        selllist = []
        daylist = []
        stockname = " "
        for day in dayIndex:
            bd = Bigdeal(code, day, volume)
            if bd.isOpen == True:
                stockname = bd.stockname
                #换算为万元
                buySum = bd.getTotalBuy() / 10000
                sellSum = bd.getTotalSell() / 10000
                buylist.append(buySum)
                selllist.append(sellSum)
                d = day.__str__().split(' ')[0]
                daylist.append(d)

        ax = plt.subplot(111)
        x = np.arange(0, len(daylist))
        x1 = x * 2.5
        x2 = x1 + 1
        plt.bar(left=x1, height=buylist, width=1, color='red')
        plt.hold
        plt.bar(left=x2, height=selllist, width=1, color='green')

        plt.xticks(x2, daylist)
        plt.legend(['buy', 'sell'], loc='upper center', fancybox=True, shadow=True)
        ax.get_yaxis().set_major_formatter(plt.FormatStrFormatter('%i'))
        # plt.setp(ax.get_xaxis().get_majorticklabels(), rotation=-45)
        myfont = matplotlib.font_manager.FontProperties(fname="/usr/share/fonts/simhei.ttf")
        yl = u'单位(万元）'
        plt.ylabel(yl, fontproperties=myfont)

        title = u"%s在%d日内超过%d手的大单交易量" % (stockname, daysNumbers, volume)
        plt.title(title, fontproperties=myfont)

        money = round(sum(buylist) - sum(selllist))
        strMoney = u"%s在%s日超过%d手的大单净流入人民币%d万元" % (stockname, daysNumbers, volume, money)
        if money < 0:
            strMoney = u"%s在%s日超过%d手的大单净流出人民币%d万元" % (stockname, daysNumbers, volume, money)
        textx = x2[0]
        texty = max([max(buylist), max(selllist)]) * 6 / 8
        plt.text(textx, texty, strMoney, fontproperties=myfont)

        plt.show()

    @staticmethod
    def numberDaysNet(code, daysNumbers, volume=500):
        #判断每天大单是净流入还是净流出
        startDay = tls.getday(-daysNumbers)
        dayIndex = pd.date_range(startDay, periods=daysNumbers + 1)
        netBigDeal = []
        daylist = []
        for day in dayIndex:
            bd = Bigdeal(code, day, volume)
            if bd.isOpen == True:
                buySum = bd.getTotalBuy()
                sellSum = bd.getTotalSell()
                flag = True
                if sellSum > buySum:
                    flag = False
                netBigDeal.append(flag)
                d = day.__str__().split(' ')[0]
                daylist.append(d)
        df = pd.DataFrame(netBigDeal, daylist)
        print(df)


if __name__ == "__main__":
    day = tls.getday(-1)
    today = datetime.date.today()
    bd = Bigdeal('600884', volume=600)
    bd.oneDayPlot()
    # Bigdeal.numberDaysPlot('000795', 5)
    # Bigdeal.numberDaysNet('000795', 5)
