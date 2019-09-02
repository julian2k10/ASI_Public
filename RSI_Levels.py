#import pdb
import time
import numpy as np
import requests
import datetime
import pandas as pd
from talib import RSI
from StockMarket.indicators import PVC
import matplotlib.pyplot as plt

class RSI_Levels():
    def __init__(self, symbol, timeframe='daily'):
        """
        parameter:
        symbol = 'AAPL', 'AMZN', etc...
        timeframe = '30min', '60min', 'daily', 'weekly', 'monthly'
        """
        self.data = {'RSI': 0, 'PRICE': 0, 'DATE': 0, 'STRENGTH': 0}
        self.stock_price_url = f"https://www.alphavantage.co/query?function={self.get_function(timeframe)}&symbol={symbol}&outputsize=full&apikey=demo&output=json"
    @property
    def set_levels(self):
        return self.data
    
    @set_levels.setter
    def set_levels(self, levels):
        self.data['RSI'] = levels['RSI']
        self.data['PRICE'] = levels['PRICE']
        self.data['DATE'] = levels['DATE']
        self.data['STRENGTH'] = levels['STRENGTH']
        
    def get_function(self, timeframe):
        if timeframe == '30min' or timeframe == '60min':
            return 'TIME_SERIES_INTRADAY'
        
        if timeframe == 'daily':
             return 'TIME_SERIES_DAILY_ADJUSTED'
            
        if timeframe == 'weekly':
             return 'TIME_SERIES_WEEKLY_ADJUSTED'
            
        if timeframe == 'monthly':
             return 'TIME_SERIES_MONTHLY_ADJUSTED'
            
    def perse_data(self, url):
        df = 'None'
        try:
            alphavantage = requests.get(url).json()
            keys = list(alphavantage.keys())
        
            if 'Meta Data' in keys:
                meta_data, data = alphavantage[keys[0]], alphavantage[keys[1]]
    
                df = pd.DataFrame.from_dict(data, orient='index', dtype=float)
                df.index.name = 'Date'
            else:
                raise Exception
        except:
            print('Server Error! will retry in 60 sec...')
            time.sleep(65)
            alphavantage = requests.get(url).json()
            keys = list(alphavantage.keys())
        
            if 'Meta Data' in keys:
                meta_data, data = alphavantage[keys[0]], alphavantage[keys[1]]
    
                df = pd.DataFrame.from_dict(data, orient='index', dtype=float)
                df.index.name = 'Date'
            else:
                df = -1
                print('ERROR getting data...')
                print(f'Server responded : \n {alphavantage[keys[0]]}')
        finally:
            return df
    
    def normalize_data(self, dataframe):
        try:
            normal_data = dict()
            for key in dataframe.keys():
                array = np.array(dataframe[key])
                array = np.nan_to_num(array)
                mean = np.mean(array)
                std = np.std(array)
                new_array = (array - mean) / std
                normal_data.update({key: new_array})

            return pd.DataFrame(normal_data)

        except:
            print('<< Incorrect Datatype Provided >>:')
            print('Datatype Expected : numpy.ndarray')
        return 'None'
#+------------------------------------------------------------------+
#|                Find Support/Resistance Levels                    |
#+------------------------------------------------------------------+
    def extract_support_resistance(self):
        """
        Extract support and resistance levels from price data
        """
        self.stock_data = self.perse_data(self.stock_price_url)
        keys = self.stock_data.keys()
        high_key = 'high'
        low_key = 'low'
        close_key = 'close'
        volume_key = 'volume'
        for key in keys:
            if high_key in key:
                high_key = key

            if low_key in key:
                low_key = key

            if close_key in key:
                close_key = key

            if volume_key in key:
                volume_key = key

        Market_Down = 'None'
        levels = list()
        temp_date = 0
        up_close_price = 0
        down_close_price = 0
        highest_close = 0
        lowest_close = 0
        strength = 0
        rsi = 0

        size = len(self.stock_data.index)
        dates = list(self.stock_data.index)
        high = self.stock_data[high_key].dropna().values
        low = self.stock_data[low_key].dropna().values
        close = self.stock_data[close_key].dropna().values
        volume = self.stock_data[volume_key].dropna().values
        _RSI = RSI(close, timeperiod=14)
        _PVC = PVC(volume, fast_period=3, slow_period=13)

        for x in range(size):
            info = self.stock_data.iloc[x]
            date = dates[x]
            price = info[close_key]
            volume = info[volume_key]

            if isinstance(Market_Down, str):
                #Market Up
                if price > up_close_price and up_close_price == 0:
                    up_close_price = price
                    
                if price > up_close_price and up_close_price > 0:
                    highest_close = price
                    Market_Down = False

                #Market Down
                if price < down_close_price and down_close_price == 0:
                    down_close_price = price
                    
                if price < down_close_price and down_close_price > 0:
                    lowest_close = price
                    Market_Down = True
            else:
                if Market_Down:
                    if price < lowest_close or lowest_close == 0:
                        lowest_close = price
                        temp_date = date
                        rsi = _RSI[x]
                        strength = _PVC[x]
                        down_close_price = 0

                    if price > lowest_close and down_close_price == 0:
                        down_close_price = price

                    if price > lowest_close and price > down_close_price and lowest_close > 0 and down_close_price > 0:
                        info = dict(self.data)
                        info['STRENGTH'] = strength
                        info['PRICE'] = lowest_close
                        info['DATE'] = temp_date
                        info['RSI'] = rsi
                        levels.append(info)
                        lowest_close = 0
                        down_close_price = 0
                        Market_Down = False
                else:
                    if price > highest_close:
                        highest_close = price 
                        temp_date = date
                        rsi = _RSI[x]
                        strength = _PVC[x]
                        up_close_price = 0
         
                    if price < highest_close and up_close_price == 0:
                        up_close_price = price
         
                    if price < highest_close and price < up_close_price:
                        info = dict(self.data)
                        info['STRENGTH'] = strength
                        info['PRICE'] = highest_close
                        info['DATE'] = temp_date
                        info['RSI'] = rsi
                        levels.append(info)
                        highest_close = 0
                        up_close_price = 0
                        Market_Down = True      
        
        prices = list(self.stock_data[close_key])
        prices_df = pd.DataFrame(list(zip(dates, prices)), columns=['Date', 'Price'])
        prices_df.set_index('Date', inplace=True, drop=True)
        prices_df.tail(100).plot(kind='line')
        plt.show()

        support_resistance = pd.DataFrame(levels)
        support_resistance.set_index('DATE', drop=True, inplace=True)

        new_df = self.normalize_data(support_resistance)
        new_df.tail(100).plot(kind='line')
        plt.show()

        print(support_resistance)

        return support_resistance

  #*************************************************************************************************

if __name__ == '__main__':
    info = RSI_Levels(symbol='SPY',timeframe='daily')
    info.extract_support_resistance()