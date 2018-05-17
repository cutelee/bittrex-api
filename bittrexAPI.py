# print under 100BTC list
# time interval: 1min -> 5min

import time
import pymysql
import datetime
from operator import itemgetter
from bittrex import Bittrex


# used api version -> version 2
API_V2_0 = 'v2.0'
bit_API = Bittrex(None, None)

# reference for trading volume(buy + sell)
btc_refer = 100


# return all markets name
def get_all_markets():
    res = bit_API.get_markets()
    success = res["success"]
    market_list = []
    if success:
        results = res["result"]         # type: list
        for result in results:
            market_list.append(result["MarketName"])

        return market_list

    else:
        print("Failed!")
        return None


# return marketName's history result
def get_market_history(MarketName):
    # can edit bit_API.get_market_history()
    res = bit_API.get_market_history(MarketName)
    success = res["success"]
    if success:
        return res["result"]
    else:
        print("Failed!")
        return None


# make string to datetime (+9 hours)
def make_datetime(timestamp):
    timestamp = timestamp.split('.')[0]
    date_time = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
    date_time = date_time.replace(second=0) + datetime.timedelta(hours=9)
    #date_time = date_time + datetime.timedelta(hours=9)
    return date_time


# select target market(under 100BTC volume) and return market_list
def check_target_market():
    markets = get_all_markets()
    market_list = []
    # check all markets and add to market_list if market is targets
    for market in markets:
        his = bit_API.get_market_history(market)
        result = get_market_history(market)
        if not result == None:
            buy = 0.0
            sell = 0.0
            standard_time = make_datetime('1970-01-01T12:00:00')

            results = his["result"]
            # check current market's all history
            for result in results:
                history_time = make_datetime(result["TimeStamp"])
                # if current history_time is larger than standard_time: renew standard_time and buy, sell sum
                if standard_time < history_time:
                    buy = 0.0
                    sell = 0.0
                    standard_time = history_time

                # if current history_time is smaller than standard_time: ignore
                if standard_time == history_time:
                    type = result["OrderType"]
                    # add time condition
                    if type == 'BUY':
                        buy += result["Total"]
                    else:
                        sell += result["Total"]

            # if total volume under 100BTC, add market_list
            if (buy+sell) < btc_refer:
                market_list.append(market)
                print(market)
                print(standard_time)
                # exception handling (divided by zero)
                if buy == 0 and sell == 0:
                    print("0 %% (%.2f / %.2f)" % (buy, buy + sell))
                else:
                    print("%.2f %% (%.2f / %.2f)" % ((buy / (buy + sell)) * 100, buy, buy + sell))

                print("Buy: ", buy)
                print("Sell: ", sell)

    return market_list


def make_last_time(market_list):
    standard_time = make_datetime('1970-01-01T12:00:00')


# get market list from 'stocks.txt' file
def get_stocks_from_file():
    fstream = open('stocks.txt', 'r')
    stocks_list = fstream.read()
    stocks = stocks_list.split(',')
    stocks.pop()        # remove last blank list
    fstream.close()
    return stocks


# write market list from 'stocks.txt' file
# get market list by using check_target_market() function
def write_stocks_to_file():
    # check target market and rewrite 'stocks.txt' file
    market_list = check_target_market()
    fstream = open('stocks.txt', 'w')
    for i in market_list:
        fstream.write(i)
        fstream.write(',')
    fstream.close()


# get param market's new 1'min interval trade data
def get_trade_data(market_name, time_dic):
    histories = get_market_history(market_name)
    if not histories == None:
        last_time = time_dic['market_name']
        checking_time = last_time
        buy = 0.0
        sell = 0.0
        sorted_histories = sorted(histories, key=itemgetter('TimeStamp'))
        for history in sorted_histories:
            # check 'is current history time is greater than last check time'
            current_time = make_datetime(history["TimeStamp"])
            if current_time > last_time:
                if current_time > checking_time:
                    if buy != 0 or sell != 0:
                        # insert db time, buy, sell, marketname
                        buy = 0.0
                        sell = 0.0

                    last_time = checking_time
                    checking_time = current_time
                    if history["OrderType"] == "BUY":
                        buy += history["Total"]
                    else:
                        sell += history["Total"]

                elif current_time == checking_time:
                    if history["OrderType"] == "BUY":
                        buy += history["Total"]
                    else:
                        sell += history["Total"]


#target_market_list = check_target_market()
#print(target_market_list)
#print(target_market_list.__len__())
target_market_list = get_stocks_from_file()
for market in target_market_list:
    get_trade_data(market)





