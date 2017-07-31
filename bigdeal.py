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
    对某只股票的大单数据进行处理和分析
    使用ts中的get_sina_dd函数获取大单数据
    """
    def __init__(self, code, day=datetime.date.today(), volume=500):
        #使用isOpen来判断是否股票是否停盘或休市
        self.isOpen = True
        dd = ts.get_sina_dd(code, day, volume)
        if dd is None:
            self.isOpen = False
        else:
            self.volume = volume
            self.stockname = dd.iloc[0, 1]
            self.day = day
            self.buy = dd[dd['type'].isin(['买盘'])]
            self.sell = dd[dd['type'].isin(['卖盘'])]

    def getTotal(self, dd):
        """
        :param dd:大单
        :return:钱数
        """
        priceVol = dd.loc[:, ['price', 'volume']]
        money = priceVol.loc[:, 'price'] * priceVol.loc[:, 'volume']
        totalmoney = sum(list(money))
        return totalmoney

    def getTotalBuy(self):
        return self.getTotal(self.buy)

    def getTotalSell(self):
        return self.getTotal(self.sell)

    def getNetBigDeal(self):
        """
        :return:净流入或流出的钱数
        """
        return self.getTotalBuy() - self.getTotalSell()

    def oneDayPlot(self, timeDelta=30):
        """
        画出某只股票某天的大单统计图
        :param timeDelta:时间间隔，单位为分钟，默认30分钟
        :return:
        """
        #matplotlib没有中文字体，需要加上，否则显示中文为乱码
        #具体的中文字体在linux中可以通过fc-list :lang=zh查看
        myfont = matplotlib.font_manager.FontProperties(fname="/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")

        dd = self.buy
        timeVol = dd.loc[:, ['time', 'volume']]
        timeVol = timeVol.sort_values(by='time')
        bigBuyDF = self.rearrange(timeVol, timeDelta)

        dd = self.sell
        timeVol = dd.loc[:, ['time', 'volume']]
        timeVol = timeVol.sort_values(by='time')
        bigSellDF = self.rearrange(timeVol, timeDelta)

        #提取时间
        timelist = []
        for t in list(bigBuyDF.iloc[:, 0]):
            strT = t[:-3]
            timelist.append(strT)

        #股票的大单数量转换为手
        blist = list(bigBuyDF.iloc[:, 1] / 100)
        slist = list(bigSellDF.iloc[:, 1] / 100)

        #开始画图
        ax = plt.subplot(111)
        x = np.arange(0, len(timelist))
        x1 = x * 2.5
        x2 = x1 + 1
        plt.bar(left=x1, height=blist, width=1, color='red')
        plt.hold
        plt.bar(left=x2, height=slist, width=1, color='green')

        plt.xticks(x2, timelist)
        plt.legend(['buy', 'sell'], loc='upper center', fancybox=True, shadow=True)
        ax.get_yaxis().set_major_formatter(plt.FormatStrFormatter('%i'))
        #ticks旋转
        # plt.setp(ax.get_xaxis().get_majorticklabels(), rotation=-45)

        yl = u'单位(手）'
        plt.ylabel(yl, fontproperties=myfont)

        title = u"%s在%s日超过%d手的大单交易量分时图" % (self.stockname, self.day, self.volume)
        plt.title(title, fontproperties=myfont)

        #获取当天的大单的净流入钱数，单位换算为万元
        money = round(self.getNetBigDeal() / 10000)
        strMoney = u"%s在%s日超过%d手的大单净流入人民币%d万元" % (self.stockname, self.day, self.volume, money)
        if money < 0:
            strMoney = u"%s在%s日超过%d手的大单净流出人民币%d万元" % (self.stockname, self.day, self.volume, money)
        textx = x1[1]
        texty = max([max(slist), max(blist)]) * 7 / 8
        plt.text(6, texty, strMoney, fontproperties=myfont)

        plt.show()

    def rearrange(self, dd, timeDelta):
        """
        统计某个时间间隔内的大单数量
        :param dd:
        :param timeDelta:
        :return:
        """

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
                    value = x - np.sum(bigDealList)
                    bigDealList.append(value)
                else:
                    bigDealList.append(x)
            else:
                bigDealList.append(0)

        bigDF = pd.DataFrame({'time': timeList, 'volume': bigDealList})

        return bigDF

    @staticmethod
    def numberDaysPlot(code, daysNumbers, volume=500):
        """
        画出某只股票从当日起，前daysNumbers天内的大单统计数据
        :param code:股票代码
        :param daysNumbers:
        :param volume:大单
        :return:
        """
        #生成天数的索引
        startDay = tls.Tools.getday(-daysNumbers)
        dayIndex = pd.date_range(startDay, periods=daysNumbers + 1)

        buylist = []
        selllist = []
        daylist = []
        stockname = " "
        for day in dayIndex:
            bd = Bigdeal(code, day, volume)
            #剔除掉休市或停牌的数据
            if bd.isOpen == True:
                stockname = bd.stockname
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
        myfont = matplotlib.font_manager.FontProperties(fname="/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc")
        yl = u'单位(万元）'
        plt.ylabel(yl, fontproperties=myfont)

        title = u"%s在%d日内超过%d手的大单交易量" % (stockname, daysNumbers, volume)
        plt.title(title, fontproperties=myfont)

        money = round(sum(buylist) - sum(selllist))
        strMoney = u"%s在%s日内超过%d手的大单净流入人民币%d万元" % (stockname, daysNumbers, volume, money)
        if money < 0:
            strMoney = u"%s在%s日内超过%d手的大单净流出人民币%d万元" % (stockname, daysNumbers, volume, money)
        textx = x2[0]
        texty = max([max(buylist), max(selllist)]) * 6 / 8
        plt.text(textx, texty, strMoney, fontproperties=myfont)

        plt.show()

    @staticmethod
    def numberDaysNet(code, daysNumbers, volume=500):
        """
        判断某只股票n天内的大单是净流入还是净流出
        :param code:
        :param daysNumbers:
        :param volume:
        :return:
        """
        startDay = tls.Tools.getday(-daysNumbers)
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
        return df


if __name__ == "__main__":
    # day = tls.Tools.getday()
    # bd = Bigdeal('000795')
    # bd.oneDayPlot()
    Bigdeal.numberDaysPlot('000795', 7)
    # Bigdeal.numberDaysNet('000795', 5)
