import os
import time
import copy
import datetime
import traceback
import matplotlib
import pandas as pd
import requests
import asi_email
import logging
import matplotlib.style
from talib import RSI, SAR
import matplotlib.pyplot as plt
from threading import *
from StockMarket import stock_evaluator_yahooFinance, manage_portfolio, market_crash_detector
plt.style.use("bmh")
root_dir = os.getcwd()#Get current working directory
MON, TUE, WED, THU, FRI, SAT, SUN = range(7) #Enumerate days of the week

def normalize_dataframe_date(dataset, column_name):
    new_dataset = dataset.copy()
    row = dataset[column_name]
    count = row.index

    for idx in count:
        date = dataset.iloc[idx][column_name]
        year = date[:4]
        month = date[5:7]
        day = date[8:10]
        hour = date[11:13]
        minute = date[14:16]

        date = year + '-' + month + '-' + day + ' ' + hour + ':' + minute
        new_dataset.at[idx, column_name] = date
    
    return new_dataset

def show_portfolio_evaluations(info):
    symbols = list(info.keys())
    data_points = 30
    
    for symbol in symbols:
        data = info[symbol]
        PRICE = data['PRICE']
        RSI = data['RSI']
        SAR = data['SAR']

        df_price = list(zip(PRICE.index, PRICE['4. close']))
        df_price = pd.DataFrame(df_price, columns=['Date', 'Close'])

        df_price = normalize_dataframe_date(df_price, 'Date')
        df_price.set_index('Date', inplace=True, drop=True)

        fig = plt.figure(1)
        plt.suptitle(f"{symbol} Price Signal")

        plt.subplot(211)
        frame1 = plt.gca()
        plt.plot(RSI[-data_points:], 'r--')
        plt.ylabel('RSI')
        plt.xticks(rotation=45, ha='right') 
        frame1.axes.get_xaxis().set_visible(False)
     
        plt.subplot(212)
        plt.plot(df_price[-data_points:], 'bo', label='PRICE')
        plt.plot(SAR[-data_points:], 'k', label='SAR')
        plt.xticks(rotation=45, ha='right')
        plt.legend(loc="upper left")
        fig.savefig(f'StockMarket/Current Positions/{symbol}.png', bbox_inches='tight')
        plt.close(fig)

def write_to_File(File_Name, data):
    with open(File_Name, 'w+') as f:
        status = f.write(str(data))
        
    return status

def read_from_File(File_Name):
    import ast
    data = 0
    try:
        with open(File_Name, 'r') as f:
            s = f.read()
            data = ast.literal_eval(s)
    except:
        print(traceback.format_exc())
        return -1
    
    return data

def isInternet_Connected():
    try:
        if requests.get('https://google.com').ok:
            return True
    except:
        return False

def is_negative_number(self, number):
        """
        Returns true if number is negative and false if number is positive.

        Keyword arguments:
        number -- interger or float value to evaluate
        """
        multiple = ['1']
        is_negative = False
        decimal_places = 0
        value = str(number)
        try:
            if '.' in value:
                value = value.split('.')
                decimal_places = len(value[1])

                for x in range(decimal_places):
                    multiple.append('0')

                multiple = ''.join(multiple)
                multiple = float(multiple)

                if float(number) * multiple < 0:
                    is_negative = True
            else:
                if float(number) < 0:
                    is_negative = True

        except Exception as ex:
            try:
                print(ex.message)
            except:
                print(ex)

        return is_negative

#Used to assign a rating value from 1 to 1000 for each operating profitability ratio
def sigmoid(self, value):
    """
    Returns a value from 1 - 1000.
    Returns 0 if input value is a negative number or input value is zero

    Keyword arguments:
    value -- interger or float value to evaluate
    """
    import math
    if self.is_negative_number(value) or value == 0:
        return 0
    else:
        return 1000 / (1 + math.exp(-value))

class Manage_Stocks_Database(Thread):
    
    def __init__ (self, thread_lock, logs):
        self.screen_lock = thread_lock
        self.logs = logs
        self.exit = False
        self.data_acquired = True
        self.symbols = stock_evaluator_yahooFinance.get_symbol_DB()
        self.industries = stock_evaluator_yahooFinance.Industries()
        self.top_growth_stocks_by_sector = stock_evaluator_yahooFinance.create_database_blueprint()
        self.top_dividend_stocks_by_sector = stock_evaluator_yahooFinance.create_database_blueprint()
        self.logger = self.logs['logger'].getLogger('ASI.Manage_Stocks_Database')
        self.sectors = ['Technology', 'Healthcare', 'Financial Services', 'Consumer Cyclical', 'Consumer Defensive', 
                        'Industrials', 'Real Estate', 'Basic Materials', 'Communication Services', 'Energy', 'Utilities']
        self.Evaluator = stock_evaluator_yahooFinance.StockExtractor(company_groups=self.industries, logs=self.logs)
        self.stock_database_state = read_from_File('manage_stock_database.txt')

        if isinstance(self.stock_database_state, dict):
            self.max_intrinsic_value = float(self.stock_database_state['max_intrinsic_value'])
            self.min_intrinsic_value = float(self.stock_database_state['min_intrinsic_value'])
            self.min_rating = float(self.stock_database_state['min_rating'])
            self.notify_users = self.stock_database_state['notify_users']
            self.industry_index = self.stock_database_state['industry_index']
            self.sector_index = self.stock_database_state['sector_index']
            self.stock_index = self.stock_database_state['stock_index']
            self.industries = self.stock_database_state['industries']
            self.sector = self.sectors[self.sector_index]

            if len(self.industries) <= 1:
                self.industries = list(self.symbols[self.sector].keys())

            top_growth_stocks_by_sector = read_from_File(f'{root_dir}/database/{self.sector}/top_growth_stocks_by_sector.txt')
            if isinstance(top_growth_stocks_by_sector, dict):
                self.top_growth_stocks_by_sector[self.sector] = top_growth_stocks_by_sector
            else:
                self.data_acquired = False

            top_dividend_stocks_by_sector = read_from_File(f'{root_dir}/database/{self.sector}/top_dividend_stocks_by_sector.txt')
            if isinstance(top_dividend_stocks_by_sector, dict):
                self.top_dividend_stocks_by_sector[self.sector] = top_dividend_stocks_by_sector
            else:
                self.data_acquired = False
            try:
                self.industry = self.industries[self.industry_index]
                self.symbol_list = self.symbols[self.sector][self.industry]
                self.symbol = self.symbol_list[self.stock_index]
                self.list_size = len(self.symbol_list)
            except:
                if self.stock_index == 0:
                    self.industries = list(self.symbols[self.sector].keys())
                    self.industry = self.industries[self.industry_index]
                    self.symbol_list = self.symbols[self.sector][self.industry]
                    self.list_size = len(self.symbol_list)
                else:
                    self.data_acquired = False
        else:
            self.data_acquired = False
        
        if not self.data_acquired:
            self.min_intrinsic_value = -800.00
            self.max_intrinsic_value = 800.00
            self.min_rating = 1400.00
            self.notify_users = False
            self.industry_index = 0
            self.sector_index = 0
            self.stock_index = 0
            self.symbol_list = list()
            self.list_size = 0
            self.industry = 'None'
            self.symbol = 'None'
            self.sector = self.sectors[self.sector_index]
            self.industries = list(self.symbols[self.sector].keys())
            self.top_growth_stocks_by_sector = stock_evaluator_yahooFinance.create_database_blueprint()
            self.top_dividend_stocks_by_sector = stock_evaluator_yahooFinance.create_database_blueprint()

        self.sorted_keys = list()
        self.results = dict()
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def save_stock_database_state(self):
        self.logger.info('Saving stock database state...\n')
        self.stock_index = 0
        if isinstance(self.stock_database_state, dict):
            self.stock_database_state.update({'industries': self.industries})
            self.stock_database_state.update({'min_rating': self.min_rating})
            self.stock_database_state.update({'notify_users': self.notify_users})
            self.stock_database_state.update({'industry_index': self.industry_index})
            self.stock_database_state.update({'sector_index': self.sector_index})
            self.stock_database_state.update({'stock_index': self.stock_index})
            self.stock_database_state.update({'min_intrinsic_value': self.min_intrinsic_value})
            self.stock_database_state.update({'max_intrinsic_value': self.max_intrinsic_value})
        else:
            self.stock_database_state = dict()
            self.stock_database_state.update({'industries': self.industries})
            self.stock_database_state.update({'min_rating': self.min_rating})
            self.stock_database_state.update({'notify_users': self.notify_users})
            self.stock_database_state.update({'industry_index': self.industry_index})
            self.stock_database_state.update({'sector_index': self.sector_index})
            self.stock_database_state.update({'stock_index': self.stock_index})
            self.stock_database_state.update({'min_intrinsic_value': self.min_intrinsic_value})
            self.stock_database_state.update({'max_intrinsic_value': self.max_intrinsic_value})

        write_to_File('manage_stock_database.txt', self.stock_database_state)

    def reset_database_state(self):
        self.stock_database_state = 0
        write_to_File('manage_stock_database.txt', self.stock_database_state)

    def update_logs(self):
        #Creates a new log file everyday
        current_time = time.time()
        asctime = str(datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d'))
        self.logs['logger'].basicConfig(level=logging.INFO,
                                        format='%(asctime)s %(name)-10s %(levelname)-8s %(message)s',
                                        datefmt='%Y-%m-%d %H:%M',
                                        filename=f'logs/{asctime} ASI log.log',
                                        filemode='a')

        self.logger = self.logs['logger'].getLogger('ASI.Manage_Stocks_Database')

    def sort_trading_universe(self, name):
        self.logger.info('Sorting Trading Universe...\n')
        file_name = f'{root_dir}/database/{name}.txt'
        trading_universe = read_from_File(file_name)
        
        if isinstance(trading_universe, dict):
            self.trading_universe = copy.deepcopy(trading_universe)
        else:
            self.logger.info('Error Importing Universe!\n')
            return False
        #Sort Trading Universe by Rating
        try:
            sectors = list(self.trading_universe.keys())
            for sector in sectors:
                if sector == 'General': continue
                trading_universe.update({sector:list()})
                for stock_info in self.trading_universe[sector]:
                    if isinstance(stock_info, dict):
                        list_size = len(trading_universe[sector])
                        size = list_size - 1
                        for x in range(list_size):
                            idx = size - x #Create reverse index
                            stock_data = trading_universe[sector][idx]
                            if stock_info['Rating'] >= stock_data['Rating']:
                                pass
                            else:
                                trading_universe[sector].insert(idx+1, stock_info)
                                break
                            if x == size:
                                trading_universe[sector].insert(idx, stock_info)
                        if list_size < 1:
                            trading_universe[sector].append(stock_info)

                self.trading_universe = copy.deepcopy(trading_universe)
        except:
            self.logger.error(traceback.format_exc())

        write_to_File(file_name, self.trading_universe)

    def update_trading_universe(self, name, sector, stock_evaluations):
        file_name = f'{root_dir}/database/{name}.txt'
        trading_universe = read_from_File(file_name)
        
        if isinstance(trading_universe, dict):
            self.trading_universe = trading_universe
        else:
            self.trading_universe = dict()
            self.trading_universe.update({'General': ['UVXY', 'SPXL']})
        
        #Update Trading Universe
        self.logger.info('Updating Universe...\n')
        industries = list(stock_evaluations[sector].keys())
        if sector not in list(self.trading_universe.keys()):
            self.trading_universe.update({sector:list()})

        for industry in industries:
            trading_universe = stock_evaluations[sector][industry]
            for stock in trading_universe:
                stock_info = dict()
                if isinstance(stock, dict):
                    stock_info.update({'Beta':stock['Beta']})
                    stock_info.update({'Symbol':stock['Symbol']})
                    stock_info.update({'Rating':stock['Rating']})
                    stock_info.update({'Intrinsic Value':stock['Intrinsic Value']})
                    stock_info.update({'Ex Dividend Date':stock['Ex Dividend Date']})
                    stock_info.update({'TTM Revenue Growth':stock['TTM Revenue Growth']})
                    stock_info.update({'TTM Stock Performance':stock['TTM Stock Performance']})
                    stock_info.update({'Revenue Growth(Annual)':stock['Revenue Growth(Annual)']})
                    stock_info.update({'Performance(Annual)':stock['Performance(Annual)']})
                    try:
                        list_size = len(list(self.trading_universe[sector]))
                        size = list_size - 1
                        for x in range(list_size):
                            stock_data = self.trading_universe[sector][x]
                            if stock_info['Symbol'] != stock_data['Symbol']:
                                pass
                            else:
                                self.trading_universe[sector][x] = stock_info
                                break
                            if x == size:
                                if stock['Rating'] != 'None' and stock['Rating'] > self.min_rating and stock['Intrinsic Value'] != 'None' and stock['Intrinsic Value'] > self.min_intrinsic_value and stock['Intrinsic Value'] < self.max_intrinsic_value and stock['Performance(Annual)'] > 5:
                                    self.trading_universe[sector].append(stock_info)

                        if list_size < 1:
                            if stock['Rating'] != 'None' and stock['Rating'] > self.min_rating and stock['Intrinsic Value'] != 'None' and stock['Intrinsic Value'] > self.min_intrinsic_value and stock['Intrinsic Value'] < self.max_intrinsic_value and stock['Performance(Annual)'] > 5:
                                self.trading_universe[sector].append(stock_info)

                    except Exception as ex:
                        self.logger.error(traceback.format_exc())

        write_to_File(file_name, self.trading_universe)
        
    def run(self):
        while not self.exit:
            localtime = time.localtime(time.time())
            self.screen_lock.acquire()
            self.update_logs()
            if self.stock_index == 0:
                self.industry = self.industries[self.industry_index]
                self.symbol_list = self.symbols[self.sector][self.industry]
                self.list_size = len(self.symbol_list)

            if self.stock_index < self.list_size:
                self.symbol = self.symbol_list[self.stock_index]
                self.logger.info("Starting Stock Evaluations...")
                self.logger.info(f'Industry #{self.industry_index+1} out of {len(self.industries)}')
                self.logger.info(f'Stock #{self.stock_index+1} out of {self.list_size}')
                self.logger.info(f'Symbol : {self.symbol}') 
                self.stock_index += 1  
                    
                #Evaluate stock
                if localtime.tm_wday >= FRI:
                    #Start realtime database updates on weekends.
                    self.Evaluator.evaluate_stock(symbol=self.symbol, realtime=True)
                else:
                    self.Evaluator.evaluate_stock(self.symbol) 
            else:
                self.stock_index = 0
                self.industry_index += 1
                file_name = f'{root_dir}/database/{self.sector}/'
                stock_evaluator_yahooFinance.sanitize_symbol_DB(self.Evaluator.get_failed_evaluations)

                #Create list of top 10 stocks for each Sector and Industry
                self.top_companies = self.Evaluator.get_growth_companies[self.industry][0:10]
                self.top_growth_stocks_by_sector[self.sector].update({self.industry:self.top_companies})
                self.update_trading_universe(name='growth_stocks_universe', sector=self.sector, stock_evaluations=self.top_growth_stocks_by_sector)
                write_to_File(file_name+'top_growth_stocks_by_sector.txt', self.top_growth_stocks_by_sector[self.sector])
                stock_evaluator_yahooFinance.sanitize_symbol_DB(self.Evaluator.get_failed_evaluations)
                self.sort_trading_universe(name='growth_stocks_universe')

                #Create list of top 10 dividend stocks from each sector
                self.top_companies = self.Evaluator.get_dividend_companies[self.industry][0:10]
                self.top_dividend_stocks_by_sector[self.sector].update({self.industry:self.top_companies})
                self.update_trading_universe(name='dividend_stocks_universe', sector=self.sector, stock_evaluations=self.top_dividend_stocks_by_sector)
                write_to_File(file_name+'top_dividend_stocks_by_sector.txt', self.top_dividend_stocks_by_sector[self.sector])
                self.sort_trading_universe(name='dividend_stocks_universe')

                self.Evaluator.reset_evaluations()
                          
            if self.industry_index >= len(self.industries):
                
                self.stock_index = 0
                self.industry_index = 0
                self.sector_index += 1
                self.logger.info(f'{self.sector} evaluations completed!!') 
                self.logger.info('creating html message...')

                file_name = f'{root_dir}/database/{self.sector}/Top {self.sector} Growth Stocks.html'
                self.sorted_keys = stock_evaluator_yahooFinance.sort_companies(self.top_growth_stocks_by_sector, self.sector)
                growth_stocks = asi_email.create_html_message(self.top_growth_stocks_by_sector[self.sector], self.sector, self.sorted_keys)
                write_to_File(file_name, growth_stocks)

                file_name = f'{root_dir}/database/{self.sector}/Top {self.sector} Dividend Stocks.html'
                self.sorted_keys = stock_evaluator_yahooFinance.sort_companies(self.top_dividend_stocks_by_sector, self.sector) 
                dividend_stocks = asi_email.create_html_message(self.top_dividend_stocks_by_sector[self.sector], self.sector, self.sorted_keys)
                write_to_File(file_name, dividend_stocks)
                
                if self.notify_users:
                    self.logger.info('html message created! sending emails...')
                    asi_email.send_html_message("Stock Market Update", html)
                if self.sector_index < len(self.sectors):
                    self.sector = self.sectors[self.sector_index]
                    self.industries = list(self.symbols[self.sector].keys())
                else:
                    self.logger.info('Stock Evaluations Completed!!')  
                    self.reset_database_state() 
                    break   

            self.screen_lock.release()          

#####################################################
##########            Getters            ############
#####################################################
    @property
    def stop(self):
        return self.exit    
        
#####################################################
##########            Setters            ############
#####################################################
    @stop.setter
    def stop(self, state):
        self.save_stock_database_state()
        self.exit = state
            
class Manage_Stocks_Portfolio(Thread):
    def __init__(self, thread_lock, logs, testing=False):
        self.exit = False
        self.logs = logs
        self.max_intrinsic_value = 100
        self.percent_change_limit = -1.50
        self.growth_stocks_percent = 0.60
        self.dividend_stocks_percent = 0.40
        self.all_sectors_negative = False
        self.all_sectors_positive = False
        self.search_3PM_opportunity = False
        self.search_10AM_opportunity = False
        self.update_portfolio = dict()
        self.evaluation_info = dict()
        self.screen_lock = thread_lock
        self.update_universe = 0
        self.robinhood = manage_portfolio.Robinhood(testing=testing)
        self.logger = self.logs['logger'].getLogger('ASI.Manage_Stocks_Portfolio')
        self.stock_portfolio_state = read_from_File('manage_stock_protfolio.txt')

        if isinstance(self.stock_portfolio_state, dict):
            self.mark_up_phase = self.stock_portfolio_state['mark_up_phase']
            self.mark_down_phase = self.stock_portfolio_state['mark_down_phase']
            self.periods_ago_limit = self.stock_portfolio_state['periods_ago_limit']
            self.accumulation_phase = self.stock_portfolio_state['accumulation_phase']
            self.distribution_phase = self.stock_portfolio_state['distribution_phase']
            self.account_risk_percent = self.stock_portfolio_state['account_risk_percent']
            self.max_position_size_percent = self.stock_portfolio_state['max_position_size_percent']
            self.sector_funds_available = self.stock_portfolio_state['sector_funds_available']
            self.intrinsic_value_limit = self.stock_portfolio_state['intrinsic_value_limit']
            self.total_portfolio_value = self.stock_portfolio_state['total_portfolio_value']
            self.position_size_percent = self.stock_portfolio_state['position_size_percent']
            self.unrecognized_symbols = self.stock_portfolio_state['unrecognized_symbols']
            self.sector_funds_weight = self.stock_portfolio_state['sector_funds_weight']
            self.total_sector_funds = self.stock_portfolio_state['total_sector_funds']
            self.total_market_value = self.stock_portfolio_state['total_market_value']
            self.total_buying_power = self.stock_portfolio_state['total_buying_power']
            self.total_free_margin = self.stock_portfolio_state['total_free_margin']
            self.exit_positions = self.stock_portfolio_state['exit_positions']
            self._sell_only = self.stock_portfolio_state['sell_only']
            self.account_profile = dict()
            self.number_of_shares = 0
            self.pending_orders = dict()
            self.server_error = list()
            self.margin_used = 0
            self.symbols = list()      
        else:
            self.max_position_size_percent = 0.15
            self.sector_funds_available = 0
            self.intrinsic_value_limit = -10
            self.total_portfolio_value = 0
            self.position_size_percent = 0.10
            self.unrecognized_symbols = 0
            self.account_risk_percent = 0.50
            self.total_sector_funds = 0
            self.total_market_value = 0
            self.total_buying_power = 0
            self.total_free_margin = 0
            self.periods_ago_limit = 15
            self.number_of_shares = 0
            self.margin_used = 0
            self._sell_only = False
            self.exit_positions = False
            #Track Market Cycles
            self.mark_up_phase = False
            self.mark_down_phase = False
            self.distribution_phase = False
            self.accumulation_phase = False
            self.account_profile = dict()
            self.pending_orders = dict()
            self.server_error = list()
            self.symbols = list()

            self.sector_funds_weight = {'Technology': 0.15, 'Consumer Cyclical': 0.12, 'Financial Services': 0.10, 'Healthcare': 0.12,
                                        'Basic Materials': 0.10, 'Consumer Defensive': 0.05, 'Industrials': 0.05, 'Energy': 0.03, 
                                        'Utilities': 0.05, 'General': 0.03, 'Communication Services': 0.05, 'Real Estate': 0.15}
        universe = dict()
        file_path = f'{root_dir}/database/'
        growth_stocks = read_from_File(file_path + 'growth_stocks_universe.txt')
        dividend_stocks = read_from_File(file_path + 'dividend_stocks_universe.txt')
        if isinstance(growth_stocks, dict) and isinstance(dividend_stocks, dict):
            try:
                del growth_stocks['None']
            except KeyError:
                pass
            try:
                del dividend_stocks['None']
            except KeyError:
                pass

            universe.update({'dividend_stocks' : dividend_stocks})
            universe.update({'growth_stocks' : growth_stocks})
            self.universe = universe
        else:
            universe.update({'dividend_stocks' : dict()})
            universe.update({'growth_stocks' : dict()})
            universe['dividend_stocks'].update({'General': ['UVXY', 'SPXL']})
            universe['growth_stocks'].update({'General': ['UVXY', 'SPXL']})
            self.logger.error('Error importing trading universe!')
            self.update_universe(universe)

        Thread.__init__(self)
        if testing == False:
            self.daemon = True
            self.start()

    def save_stock_portfolio_state(self):
        self.logger.info('Saving stock portfolio state...\n')
        if isinstance(self.stock_portfolio_state, dict):
            self.stock_portfolio_state.update({'sell_only': self.sell_only})
            self.stock_portfolio_state.update({'exit_positions': self.exit_positions})
            self.stock_portfolio_state.update({'max_position_size_percent': self.max_position_size_percent})
            self.stock_portfolio_state.update({'sector_funds_available': self.sector_funds_available})
            self.stock_portfolio_state.update({'intrinsic_value_limit': self.intrinsic_value_limit})
            self.stock_portfolio_state.update({'total_portfolio_value': self.total_portfolio_value})
            self.stock_portfolio_state.update({'position_size_percent': self.position_size_percent})
            self.stock_portfolio_state.update({'unrecognized_symbols': self.unrecognized_symbols})
            self.stock_portfolio_state.update({'account_risk_percent': self.account_risk_percent})
            self.stock_portfolio_state.update({'sector_funds_weight': self.sector_funds_weight})
            self.stock_portfolio_state.update({'total_sector_funds': self.total_sector_funds})
            self.stock_portfolio_state.update({'total_market_value': self.total_market_value})
            self.stock_portfolio_state.update({'total_buying_power': self.total_buying_power})
            self.stock_portfolio_state.update({'accumulation_phase': self.accumulation_phase}) 
            self.stock_portfolio_state.update({'distribution_phase': self.distribution_phase})  
            self.stock_portfolio_state.update({'total_free_margin': self.total_free_margin})
            self.stock_portfolio_state.update({'periods_ago_limit': self.periods_ago_limit})  
            self.stock_portfolio_state.update({'mark_down_phase': self.mark_down_phase}) 
            self.stock_portfolio_state.update({'mark_up_phase': self.mark_up_phase})      
        else:
            self.stock_portfolio_state = dict()
            self.stock_portfolio_state.update({'sell_only': self.sell_only})
            self.stock_portfolio_state.update({'exit_positions': self.exit_positions})
            self.stock_portfolio_state.update({'max_position_size_percent': self.max_position_size_percent})
            self.stock_portfolio_state.update({'sector_funds_available': self.sector_funds_available})
            self.stock_portfolio_state.update({'intrinsic_value_limit': self.intrinsic_value_limit})
            self.stock_portfolio_state.update({'total_portfolio_value': self.total_portfolio_value})
            self.stock_portfolio_state.update({'position_size_percent': self.position_size_percent})
            self.stock_portfolio_state.update({'unrecognized_symbols': self.unrecognized_symbols})
            self.stock_portfolio_state.update({'account_risk_percent': self.account_risk_percent})
            self.stock_portfolio_state.update({'sector_funds_weight': self.sector_funds_weight})
            self.stock_portfolio_state.update({'total_sector_funds': self.total_sector_funds})
            self.stock_portfolio_state.update({'total_market_value': self.total_market_value})
            self.stock_portfolio_state.update({'total_buying_power': self.total_buying_power})
            self.stock_portfolio_state.update({'accumulation_phase': self.accumulation_phase}) 
            self.stock_portfolio_state.update({'distribution_phase': self.distribution_phase})  
            self.stock_portfolio_state.update({'total_free_margin': self.total_free_margin})
            self.stock_portfolio_state.update({'periods_ago_limit': self.periods_ago_limit})  
            self.stock_portfolio_state.update({'mark_down_phase': self.mark_down_phase}) 
            self.stock_portfolio_state.update({'mark_up_phase': self.mark_up_phase})
            
        write_to_File('manage_stock_protfolio.txt', self.stock_portfolio_state)

    def update_logs(self):
        #Creates a new log file everyday
        current_time = time.time()
        asctime = str(datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d'))
        self.logs['logger'].basicConfig(level=logging.INFO,
                                        format='%(asctime)s %(name)-10s %(levelname)-8s %(message)s',
                                        datefmt='%Y-%m-%d %H:%M',
                                        filename=f'logs/{asctime} ASI log.log',
                                        filemode='a')

        self.logger = self.logs['logger'].getLogger('ASI.Manage_Stocks_Portfolio')
        
    def delete_stock(self, stock_list, symbol):
        idx = 0
        stock_found = False
        for x in range(len(stock_list)):
            stock_info = stock_list[x]
            if stock_info['symbol'] == symbol:
                stock_found = True
                idx = x
                break
        if stock_found:
            del stock_list[idx]

        return copy.deepcopy(stock_list)

    def open_position(self, symbol, quantity, price):
        results = None
        try:
            valid_order = True
            try:
                if quantity <= 0:
                    self.logger.error("Invalid Order Quantity!")
                    valid_order = False
                else:
                    quantity = int(quantity)
            except:
                self.logger.error("Invalid Order Quantity!")
                valid_order = False
            try:
                if price <= 0:
                    self.logger.error("Invalid Order Price!")
                    valid_order = False
                else:
                    price = round(float(price), 2)
            except:
                self.logger.error("Invalid Order Price!")
                valid_order = False

            if not isinstance(symbol, str):
                self.logger.error("Invalid Order Symbol!")
                valid_order = False

            if valid_order:
                if symbol not in list(self.pending_orders.keys()):
                    results = self.robinhood.order_buy_limit(symbol=symbol, quantity=quantity, limitPrice=price)
                    keys = list(results.keys())
                    reason = 'None'
                    if 'id' in keys: 
                        order_id = results['id']
                        if symbol not in self.symbols : self.symbols.append(symbol)
                        self.logger.info(f'<< Bought {quantity} shares of {symbol} at ${price}! >>')
                        self.pending_orders.update({symbol:{'quantity':quantity, 'price':price, 'side':'buy', 'id':order_id}})
                        results = True
                    else: 
                        try:
                            reason = results['detail']
                        except:
                            reason = ''
                        self.logger.error(f"Error buying {quantity} shares of {symbol} at ${price}! {reason}")
                        results = False
                else:
                    self.logger.warning(f'Limit Order for {symbol} Not Filled! Converting to Market Order...')
                    self.robinhood.cancel_stock_orders(symbol=symbol)
                    results = self.robinhood.order_buy_market(symbol=symbol, quantity=quantity)
                    keys = list(results.keys())
                    reason = ''
                    if 'id' in keys: 
                        order_id = results['id']
                        self.logger.info(f'<< Bought {quantity} shares of {symbol} at ${price}! >>')
                        self.pending_orders.update({symbol:{'quantity':quantity, 'price':price, 'side':'buy', 'id':order_id}})
                        results = True
                    else: 
                        if 'detail' in keys:
                            reason = results['detail']
                        self.logger.error(f"Error buying {quantity} shares of {symbol} at ${price}! {reason}")
                        results = False
        except:
            self.logger.error(f'<<Error buying {quantity} shares of {symbol} at ${price}!>> \nManual Override Required! \nAn error occur when buying {quantity} shares of {symbol} at ${price}')
            text = f'<<Error buying {quantity} shares of {symbol} at ${price}!>>'
            html = f'<html> <h1>Manual Override Required!</h1> \n<p>An error occur when buying {quantity} shares of {symbol} at ${price}</p></html>'
            asi_email.send_html_message(text, html)
            self.logger.error(traceback.format_exc())
            results = False

        finally:
            return results
 
    def close_position(self, symbol, quantity, price):
        results = None
        try:
            valid_order = True
            try:
                if quantity <= 0:
                    self.logger.error("Invalid Order Quantity!")
                    valid_order = False
                else:
                    quantity = int(quantity)
            except:
                self.logger.error("Invalid Order Quantity!")
                valid_order = False
            try:
                if price <= 0:
                    self.logger.error("Invalid Order Price!")
                    valid_order = False
                else:
                    price = round(float(price), 2)
            except:
                self.logger.error("Invalid Order Price!")
                valid_order = False

            if not isinstance(symbol, str):
                self.logger.error("Invalid Order Symbol!")
                valid_order = False

            if valid_order:
                if symbol not in list(self.pending_orders.keys()):
                    results = self.robinhood.order_sell_limit(symbol=symbol, quantity=quantity, limitPrice=price)
                    keys = list(results.keys())
                    reason = ''
                    if 'id' in keys: 
                        order_id = results['id']
                        self.logger.info(f'<< Sold {quantity} shares of {symbol} at ${price}! >>') 
                        self.pending_orders.update({symbol:{'quantity':quantity, 'price':price, 'side':'sell', 'id':order_id}})
                        results = True
                    else: 
                        if 'detail' in keys:
                            reason = results['detail']
                        self.logger.error(f"Error selling {quantity} shares of {symbol} at ${price}! {reason}")
                        results = False
                else:
                    self.logger.warning(f'Limit Order at for {symbol} Not Filled! Converting to Market Order...')
                    self.robinhood.cancel_stock_orders(symbol=symbol)
                    results = self.robinhood.order_sell_market(symbol=symbol, quantity=quantity)
                    keys = list(results.keys())
                    reason = ''
                    if 'id' in keys: 
                        order_id = results['id']
                        self.logger.info(f'<< Sold {quantity} shares of {symbol} at ${price}! >>') 
                        self.pending_orders.update({symbol:{'quantity':quantity, 'price':price, 'side':'sell', 'id':order_id}})
                        results = True
                    else: 
                        if 'detail' in keys:
                            reason = results['detail']
                        self.logger.error(f"Error selling {quantity} shares of {symbol} at ${price}! {reason}")
                        results = False
        except:
            self.logger.error(traceback.format_exc())
            try:
                self.robinhood.cancel_stock_orders(symbol=symbol)
                results = self.robinhood.order_sell_limit(symbol=symbol, quantity=quantity, limitPrice=price)
                keys = list(results.keys())
                reason = ''
                if 'id' in keys: 
                    order_id = results['id']
                    self.logger.info(f'<< Sold {quantity} shares of {symbol} at ${price}! >>') 
                    self.pending_orders.update({symbol:{'quantity':quantity, 'price':price, 'side':'sell', 'id':order_id}})
                    results = True
                else: 
                    if 'detail' in keys:
                        reason = results['detail']
                    self.logger.error(f"Error selling {quantity} shares of {symbol} at ${price}! {reason}")
                    results = False
            except:
                self.logger.error(f'<<Error Closing {symbol} Order!>> \nManual Override Required! \nAn error occur when selling {quantity} shares of {symbol} at ${price}')
                text = f'<<Error Closing {symbol} Order!>>'
                html = f'<html> <h1>Manual Override Required!</h1> \n<p>An error occur when selling {quantity} shares of {symbol} at ${price}</p></html>'
                asi_email.send_html_message(text, html)
                results = False

        return results
       
    def rebalance_portfolio(self, universe, testing=False):
        """
        Summary:
            Divide funds equally among active positions, and sell excess stocks or stocks not in trading universe

        Keyword arguments: 
        universe -- string : name of trading universe(i.e 'dividend_stocks' or 'growth_stocks')
        testing -- bool : default = False; only used for unit-testing

        Return: 
        positions_removed -- int : number of positions that was closed.
        positions -- dict : dictionary of stocks that was sold to freeup funds and list of stocks that was bought.
        """
        positions = dict()
        ignore_list = list()
        positions_removed =  0
        growth_stocks_list = list()
        dividend_stocks_list = list()
        try:
            print()# Create newline in log file
            if not testing : self.update_sector_funds()
            else : self.logger.info("Using Testing Data...")
            if isinstance(self.universe, dict):
                try:
                    # Create stock lists and ignore list
                    for sector in list(self.universe['growth_stocks'].keys()):
                        stocks = self.universe['growth_stocks'][sector]
                        for stock_info in stocks:
                            if isinstance(stock_info, dict):
                                symbol = stock_info['Symbol']
                                growth_stocks_list.append(symbol)

                    for sector in list(self.universe['dividend_stocks'].keys()):
                        stocks = self.universe['dividend_stocks'][sector]
                        for stock_info in stocks:
                            if isinstance(stock_info, dict):
                                symbol = stock_info['Symbol']
                                dividend_stocks_list.append(symbol)

                    ignore_list.extend(self.universe['dividend_stocks']['General'])
                    ignore_list.extend(self.universe['growth_stocks']['General'])
                    ignore_list = list(set(ignore_list))
                except:
                    self.logger.error(traceback.format_exc())
            # Close all positions not in trading universe
            if isinstance(self.unrecognized_symbols, list) and len(self.unrecognized_symbols) > 0:
                print()# Create newline in log file
                self.logger.warning('Closing Unrecognized Positions...\n')
                symbols = self.unrecognized_symbols
                current_positions = list(self.portfolio.keys())
                self.unrecognized_symbols = list()
                for symbol in symbols:
                    if symbol in current_positions:
                        stock_info = self.portfolio[symbol]
                        quantity = stock_info['quantity']
                        equity = float(stock_info['equity'])
                        average_cost = float(stock_info['average_buy_price'])
                        price = round(float(stock_info['price']), 2)
                        if '.' in quantity:
                            quantity = stock_info['quantity'].split('.')
                            quantity = int(quantity[0])
                        else:
                            quantity = stock_info['quantity']
                            quantity = int(quantity)
                        if equity > 0:
                            if price >= average_cost:
                                if not testing : self.close_position(symbol=symbol, quantity=quantity, price=price)
                                else: self.logger.info(f'<< Sold {quantity} shares of {symbol} at ${price}! >>')
                                positions[symbol] = -quantity
                                positions_removed += 1
                            else:
                                self.logger.info(f"Waiting for better market conditions to sell {quantity} shares of {symbol}...")
                        else:
                            if not testing : self.robinhood.cancel_stock_orders(symbol=symbol)
                            else: self.logger.info(f"{symbol} Order Canceled!")
                            positions[symbol] = 0
                print()# Create newline in log file
                if not testing : self.update_sector_funds()
        except:
            self.logger.error(traceback.format_exc())
        # Sell excess stocks and add more stocks to position.
        try:
            self.logger.info('Rebalancing Portfolio...\n')
            for sector in list(self.universe[universe].keys()):
                stocks = list()
                symbol_list = self.universe[universe][sector]
                free_equity = copy.deepcopy(self.sector_funds_available[universe][sector])
                # Get stock evaluations and account holdings for all stocks in the selected sector
                if sector == 'General' : continue
                for symbol_info in symbol_list:
                    symbol = symbol_info['Symbol']
                    rating = symbol_info['Rating']
                    intrinsic_value = symbol_info['Intrinsic Value']
                    if symbol in self.symbols:
                        info = self.portfolio[symbol]
                        stocks.append({'symbol':symbol, 'rating':rating, 'intrinsic_value':intrinsic_value, 'quantity':info['quantity'], 'price':info['price'], 'average_buy_price':info['average_buy_price'], 'equity':info['equity']})
                
                weak_stocks = self.sort_by_rating(dataset=stocks, order='descending')# Sort with weaker stocks at top of list
                max_equity = self.total_sector_funds[universe][sector] * self.max_position_size_percent
                desired_equity = self.total_sector_funds[universe][sector] * self.position_size_percent
                self.logger.info(f'Rebalancing {sector} Stocks...\n')
                self.logger.info(f'Available Sector Funds : {round(free_equity, 2)}')
                self.logger.info(f'Max Equity : {round(max_equity, 2)} | Desired Equity : {round(desired_equity, 2)}')
                # Sell excess stocks
                for stock_info in weak_stocks:
                    symbol = stock_info['symbol']
                    quantity = stock_info['quantity']
                    equity = float(stock_info['equity'])
                    average_cost = float(stock_info['average_buy_price'])
                    price = round(float(stock_info['price']), 2)
                    if equity <= max_equity : continue
                    if '.' in quantity:
                        quantity = stock_info['quantity'].split('.')
                        quantity = int(quantity[0])
                    else:
                        quantity = int(quantity)
                    if quantity > 1:
                        max_quantity = int(max_equity / price)
                        quantity = quantity - max_quantity
                        if equity > 0: # Not pending order
                            if quantity > 0:
                                if price >= average_cost:
                                    if not testing:
                                        results = self.close_position(symbol=symbol, quantity=quantity, price=price)
                                        if isinstance(results, bool) and results:
                                            positions[symbol] = -quantity
                                            equity = price * quantity
                                            free_equity += equity
                                    else: 
                                        positions[symbol] = -quantity                                       
                                        equity = price * quantity
                                        free_equity += equity
                                        self.logger.info(f'<< Sold {quantity} shares of {symbol} at ${price}! >>')
                                else:
                                    self.logger.info(f"Waiting for better market conditions to sell {quantity} shares of {symbol}...")
                        else:
                            self.logger.info(f"Waiting for {symbol} order to execute...")
                print()# Create newline in log file
                if self.sell_only:
                    self.logger.warning("SELL_ONLY_MODE")
                    return (positions_removed, positions)
                # Strategically increase position size for strong companies
                strong_stocks = self.sort_by_rating(dataset=stocks, order='ascending')# Sort with stronger stocks at top of list
                for stock_info in strong_stocks:
                    symbol = stock_info['symbol']
                    rating = stock_info['rating']
                    quantity = stock_info['quantity']
                    equity = float(stock_info['equity'])
                    price = round(float(stock_info['price']), 2)
                    average_cost = float(stock_info['average_buy_price'])
                    if equity >= desired_equity : continue
                    new_equity = desired_equity - equity
                    if new_equity < free_equity:
                        quantity = int(new_equity / price)
                        if quantity > 0 and not self.sell_only:
                            if not testing:
                                results = self.open_position(symbol=symbol, quantity=quantity, price=price)
                                if isinstance(results, bool) and results:
                                    positions[symbol] = quantity
                                    equity = price * quantity
                                    free_equity -= equity
                            else: 
                                positions[symbol] = quantity
                                equity = price * quantity
                                free_equity -= equity
                                self.logger.info(f'<< Bought {quantity} more shares of {symbol} at ${price}! >>')
                    else:
                        # Check how much equity can be freed before selling any stocks.
                        freeable_funds = self.max_freeable_funds(positions_info=weak_stocks, stock_rating=rating)
                        self.logger.info(f'Max Freeable Funds : {freeable_funds}')
                        # Sell weaker companies to freeup funds for new position
                        if price < freeable_funds:
                            self.logger.info('Reallocating Funds...\n')
                            positions_added = False
                            stocks = copy.deepcopy(weak_stocks)
                            for idx in range(len(stocks)):
                                stock = stocks[idx]
                                _symbol = stock['symbol']
                                _quantity = stock['quantity']
                                _equity = float(stock['equity'])
                                _rating = float(stock['rating'])
                                _price = round(float(stock['price']), 2)
                                _average_buy_price = float(stock['average_buy_price'])
                                _side = 'None'
                                if _symbol in list(self.pending_orders.keys()):
                                    stock_data = self.pending_orders[_symbol]
                                    _price = float(stock_data['price'])
                                    _quantity = stock_data['quantity']
                                    _side = stock_data['side']
                                    _equity = _price * _quantity
                                try:
                                    if '.' in _quantity:
                                        _quantity = _quantity.split('.')
                                        _quantity = int(_quantity[0])
                                    else:
                                        _quantity = int(_quantity)
                                    # Start selling weak companies until there is enough free equity to open the new position.
                                    total_equity = free_equity + equity
                                    if total_equity < desired_equity:
                                        if _symbol in list(self.pending_orders.keys()):
                                            if _side == 'buy': 
                                                if not testing:
                                                    self.robinhood.cancel_stock_orders(symbol=_symbol)
                                                free_equity += _equity
                                                positions[_symbol] = 0
                                        else:
                                            if _price > _average_buy_price and _rating < rating:
                                                if _quantity > 1:
                                                    if (_equity + total_equity) > desired_equity:
                                                        new_quantity = 0
                                                        for x in range(_quantity):
                                                            new_quantity += 1
                                                            free_equity += _price
                                                            total_equity = free_equity + equity
                                                            if total_equity >= desired_equity:
                                                                _quantity = new_quantity
                                                                break
                                                    else:
                                                        free_equity += _equity
                                                else:
                                                    free_equity += _equity
                                                if not testing : 
                                                    results = self.close_position(symbol=_symbol, quantity=_quantity, price=_price)
                                                    if isinstance(results, bool) and results: 
                                                        positions[_symbol] = -_quantity
                                                        weak_stocks = self.delete_stock(stock_list=weak_stocks, symbol=_symbol)
                                                        self.sector_funds_available[universe][sector] = copy.deepcopy(free_equity)
                                                else: 
                                                    positions[_symbol] = -_quantity
                                                    weak_stocks = self.delete_stock(stock_list=weak_stocks, symbol=_symbol) 
                                                    self.sector_funds_available[universe][sector] = copy.deepcopy(free_equity)
                                                    self.logger.info(f'<< Sold {_quantity} shares of {_symbol} at ${_price}! >>')
                                    else:
                                        # Add more stocks to stronger positions
                                        new_equity = desired_equity - equity
                                        if new_equity < free_equity:
                                            quantity = int(new_equity / price)
                                            if quantity > 0 and not self.sell_only:
                                                if not testing :
                                                    results = self.open_position(symbol=symbol, quantity=quantity, price=price)
                                                    if isinstance(results, bool) and results:
                                                        positions_added = True
                                                        positions[symbol] = quantity
                                                        equity = price * quantity
                                                        free_equity -= equity
                                                        break
                                                else: 
                                                    positions_added = True
                                                    positions[symbol] = quantity
                                                    equity = price * quantity
                                                    free_equity -= equity
                                                    self.logger.info(f'<< Bought {quantity} more shares of {symbol} at ${price}! >>')
                                                    break
                                        else:
                                            new_equity = free_equity
                                            quantity = int(new_equity / price)
                                            if quantity > 0 and not self.sell_only:
                                                if not testing :
                                                    results = self.open_position(symbol=symbol, quantity=quantity, price=price)
                                                    if isinstance(results, bool) and results:
                                                        positions_added = True
                                                        positions[symbol] = quantity
                                                        equity = price * quantity
                                                        free_equity -= equity
                                                        break
                                                else: 
                                                    positions_added = True
                                                    positions[symbol] = quantity
                                                    equity = price * quantity
                                                    free_equity -= equity
                                                    self.logger.info(f'<< Bought {quantity} more shares of {symbol} at ${price}! >>')
                                                    break
                                except :
                                    self.logger.error(traceback.format_exc())
                            # Use funds available to add to position
                            if positions_added == False:
                                new_equity = free_equity
                                quantity = int(new_equity / price)
                                if quantity > 0 and not self.sell_only:
                                    if not testing :
                                        results = self.open_position(symbol=symbol, quantity=quantity, price=price)
                                        if isinstance(results, bool) and results:
                                            positions_added = True
                                            positions[symbol] = quantity
                                            equity = price * quantity
                                            free_equity -= equity
                                    else: 
                                        positions_added = True
                                        positions[symbol] = quantity
                                        equity = price * quantity
                                        free_equity -= equity
                                        self.logger.info(f'<< Bought {quantity} more shares of {symbol} at ${price}! >>')
                        else:
                            if freeable_funds == 0:
                                print()# Create newline in log file
                                break
                self.sector_funds_available[universe][sector] = copy.deepcopy(free_equity)
        except :
            self.logger.error(traceback.format_exc())

        return (positions_removed, positions)
        
    def max_freeable_funds(self, positions_info, stock_rating):
        idx = len(positions_info) - 1
        max_equity = 0
        while idx > 0:
            try:
                stock_info = positions_info[idx]
                idx -= 1
                symbol = stock_info['symbol']
                price = float(stock_info['price'])
                rating = float(stock_info['rating'])
                average_buy_price = float(stock_info['average_buy_price'])
                if symbol in list(self.pending_orders.keys()):
                    stock_info = self.pending_orders[symbol]
                    quantity = stock_info['quantity']
                    price = float(stock_info['price'])
                    side = stock_info['side']
                    if side == 'buy':
                        equity = price * quantity
                    else:
                        equity = 0
                else:
                    equity = float(stock_info['equity'])

                if price > average_buy_price and rating < stock_rating:
                    max_equity += equity
            except:
                self.logger.error(traceback.format_exc())
                return -1

        return max_equity

    def sort_by_rating(self, dataset, order='ascending'):
        try:
            new_dataset = list()
            for stock_info in dataset:
                if isinstance(stock_info, dict):
                    list_size = len(new_dataset)
                    size = list_size - 1
                    for x in range(list_size):
                        idx = size - x #Create reverse index
                        stock_data = new_dataset[idx]
                        if stock_info['rating'] >= stock_data['rating']:
                            pass
                        else:
                            new_dataset.insert(idx+1, stock_info)
                            break
                        if x == size:
                            new_dataset.insert(idx, stock_info)
                    if list_size < 1:
                        new_dataset.append(stock_info)

            if isinstance(order, str):
                if order == 'ascending':
                    return copy.deepcopy(new_dataset)
                elif order == 'descending':
                    descending = new_dataset[::-1]
                    return copy.deepcopy(descending)
                else:
                    self.logger.error(f"Invalid Parameter order='{order}'")
            else:
                self.logger.error(f"Invalid Datatype! {type(order)} \nExpected Datatype: {type(str)}")
        except:
            self.logger.error(traceback.format_exc())

    def reallocate_funds(self, universe, sector, stock_price, stock_symbol, testing=False):
        """
        Sell excess stocks to free up funds for new position

        Parameters: 
        universe -- string : name of trading universe(i.e 'dividend_stocks' or 'growth_stocks')
        sector -- string : sector of the selected stock
        stock_price -- float : stock price of the new position
        stock_symbol -- string : ticker/symbol for the new position
        testing -- bool : default = False; only used for unit-testing

        Return: 
        number_of_shares -- int : number of shares available funds can buy.
        positions -- dict : dictionary of stocks that was sold to freeup funds
        """
        try:
            print()#Create newline in log file
            self.logger.info('Building Portfolio...\n')
            if not testing:
                self.portfolio = self.robinhood.build_holdings()
                self.symbols = list(self.portfolio.keys())
            else:
                self.symbols = list(self.portfolio.keys())
            try:
                #Delete pending orders from list after it executes.
                orders = list(self.pending_orders.keys())
                open_positions = list(self.portfolio.keys())
                for symbol in orders:
                    if symbol in open_positions:
                        stock_info = self.portfolio[symbol]
                        if float(stock_info['equity']) > 0: 
                            if (stock_info['equity']['id'] == self.pending_orders[symbol]['id']):
                                print(f'Deleting {symbol} Pending Order...')
                                del self.pending_orders[symbol]
                            else:
                                print("Order id DO NOT MATCH!")
                                print(f"stock_info['id'] : {stock_info['id']}")
                                print(f"self.pending_orders[symbol]['id'] : {self.pending_orders[symbol]['id']}")
                    else:
                        print(f'Deleting {symbol} Pending Order...')
                        del self.pending_orders[symbol]
            except:
                self.logger.error(traceback.format_exc())
        except:
            self.logger.error(traceback.format_exc())

        positions = dict()
        stock_info = list()
        number_of_shares = 0
        new_position_info = dict()
        symbol_list = self.universe[universe][sector]
        free_equity = self.sector_funds_available[universe][sector]
        #Get stock evaluation for new position and all other portfolio positions in the selected sector
        for symbol_info in symbol_list:
            symbol = symbol_info['Symbol']
            rating = symbol_info['Rating']
            intrinsic_value = symbol_info['Intrinsic Value']
            if symbol == stock_symbol:
                new_position_info = {'symbol':symbol , 'rating':rating, 'intrinsic_value': intrinsic_value}

            if symbol in self.symbols:
                info = self.portfolio[symbol]
                stock_info.append({'symbol':symbol, 'rating':rating, 'intrinsic_value':intrinsic_value, 'quantity':info['quantity'], 'price':info['price'], 'average_buy_price':info['average_buy_price'], 'equity':info['equity']})
        
        stock_info = self.sort_by_rating(dataset=stock_info, order='descending')
        #Check how much equity can be freed before selling any stocks.
        freeable_funds = self.max_freeable_funds(positions_info=stock_info, stock_rating=new_position_info['rating'])
        self.logger.info(f'{sector} sector has {len(stock_info)} active positions!')
        current_positions = list()
        for stock in stock_info:
            current_positions.append(stock['symbol'])
        self.logger.info(f"{current_positions}\n")
        self.logger.info(f'Available Sector Funds : {round(free_equity, 2)} | Max Freeable Funds : {freeable_funds}')
        print()#Create newline in log file
        #Sell weak performing stocks to freeup funds for new position
        if stock_price < freeable_funds:
            self.logger.info('Reallocating Funds...\n')
            for stock in stock_info:
                symbol = stock['symbol']
                quantity = stock['quantity']
                equity = float(stock['equity'])
                rating = float(stock['rating'])
                price = round(float(stock['price']), 2)
                average_buy_price = float(stock['average_buy_price'])
                side = 'None'
                if symbol in list(self.pending_orders.keys()):
                    stock_data = self.pending_orders[symbol]
                    price = float(stock_data['price'])
                    quantity = stock_data['quantity']
                    side = stock_data['side']
                    equity = price * quantity
                try:
                    if '.' in quantity:
                        quantity = stock['quantity'].split('.')
                        quantity = int(quantity[0])
                    else:
                        quantity = int(quantity)
                    #Start selling stocks until there is enough free equity to open the new position.
                    if free_equity < stock_price:
                        if symbol in list(self.pending_orders.keys()):
                            if side == 'buy': 
                                if not testing : self.robinhood.cancel_stock_orders(symbol=symbol)
                                else : self.logger.info(f"{symbol} Order Canceled!")
                                positions[symbol] = 0
                                free_equity += equity
                        else:
                            if price > average_buy_price and rating < new_position_info['rating']:
                                if quantity > 1:
                                    if (equity + free_equity) > stock_price:
                                        new_quantity = 0
                                        for x in range(quantity):
                                            new_quantity += 1
                                            free_equity += price
                                            if free_equity >= stock_price:
                                                quantity = new_quantity
                                                break
                                    else:
                                        free_equity += equity
                                else:
                                    free_equity += equity
                                if not testing : self.close_position(symbol=symbol, quantity=quantity, price=price)
                                else : self.logger.info(f'<< Sold {quantity} shares of {symbol} at ${price}! >>') 
                                positions[symbol] = -quantity
                    else:
                        self.sector_funds_available[universe][sector] = copy.deepcopy(free_equity)
                        number_of_shares = 1
                        print()#Create newline in log file
                        break
                except :
                    self.logger.error(traceback.format_exc())
            
        return (number_of_shares, positions)                       

    def get_symbol_rank(self, universe, sector, symbol):
        idx = 1
        symbols_list = list(self.universe[universe][sector])
        for symbol_info in symbols_list:
            sym = symbol_info['Symbol']
            if sym == symbol:
                return idx
            idx += 1

        return idx

    def update_sector_funds(self):
        self.total_market_value = 0
        try:
            self.logger.info('Building Portfolio...\n')
            self.account_profile = self.robinhood.get_accounts_profile()
            self.portfolio = self.robinhood.build_holdings()
            self.symbols = list(self.portfolio.keys())
            try:
                #Delete pending orders from list after it executes.
                orders = list(self.pending_orders.keys())
                positions = list(self.portfolio.keys())
                for symbol in orders:
                    if symbol in positions:
                        stock_info = self.portfolio[symbol]
                        if float(stock_info['equity']) > 0: 
                            if (stock_info['equity']['id'] == self.pending_orders[symbol]['id']):
                                print(f'Deleting {symbol} pending order...')
                                del self.pending_orders[symbol]
                            else:
                                print(f"stock_info['id'] : {stock_info['id']}")
                                print(f"self.pending_orders[symbol]['id'] : {self.pending_orders[symbol]['id']}")
                    else:
                        print(f'Deleting {symbol} pending order...')
                        del self.pending_orders[symbol]
            except:
                pass

            self.logger.info('Updating Sector Funds...\n')
            if isinstance(self.account_profile, dict) and isinstance(self.portfolio, dict):
                margin_info = self.account_profile['margin_balances']
                self.margin_used = float(margin_info['cash']) + float(margin_info['unsettled_funds'])
                self.total_buying_power = float(margin_info['day_trade_buying_power']) + float(margin_info['overnight_buying_power'])

                self.total_sector_funds = dict()
                self.total_sector_funds.update({'dividend_stocks' : dict()})
                self.total_sector_funds.update({'growth_stocks' : dict()})

                for symbol in self.symbols:
                    equity = float(self.portfolio[symbol]['equity'])
                    self.total_market_value += round(equity, 2)
                    if symbol == 'UVXY': 
                        self.inverse_equity = round(equity, 2)

                keys = list(self.universe['dividend_stocks'].keys())
                for key in keys:
                    self.total_sector_funds['dividend_stocks'].update({key : 0.00})
                    self.total_sector_funds['growth_stocks'].update({key : 0.00})

                self.sector_funds_available = copy.deepcopy(self.total_sector_funds)
            else:
                self.logger.error('Error Updating Sector Funds Available!')
                return False
            
        except Exception:
            self.logger.error(traceback.format_exc())
            return False

        if isinstance(self.universe, dict):
            ##############################################################################
            ###################             Dividend Stocks           ####################
            ##############################################################################
            try:
                sectors = list(self.universe['dividend_stocks'].keys())
                for sector in sectors:
                    symbols_list = self.universe['dividend_stocks'][sector]
                    for stock_info in symbols_list:
                        if isinstance(stock_info, dict):
                            symbol = stock_info['Symbol']
                            intrinsic_value = stock_info['Intrinsic Value']
                            ex_dividend_date = stock_info['Ex Dividend Date']
                        else:
                            symbol = stock_info
                            intrinsic_value = 'None'
                            ex_dividend_date = 'None'

                        if symbol in self.symbols:
                            #Add intrinsic value to active portfolio positions.
                            if isinstance(self.portfolio, dict):
                                self.portfolio[symbol]['intrinsic_value'] = intrinsic_value
                                self.portfolio[symbol]['ex_dividend_date'] = ex_dividend_date
                            try:
                                equity = float(self.portfolio[symbol]['equity'])
                                self.sector_funds_available['dividend_stocks'][sector] -= round(equity, 2)
                                if symbol in list(self.pending_orders.keys()) and self.pending_orders[symbol]['side'] == 'buy':
                                    equity = self.pending_orders[symbol]['price'] * self.pending_orders[symbol]['quantity']
                                    self.sector_funds_available['dividend_stocks'][sector] -= round(equity, 2)

                            except Exception:
                                self.logger.error(traceback.format_exc())
                                return False

                self.total_portfolio_value = self.total_market_value + self.total_buying_power
                self.total_free_margin = self.total_portfolio_value * self.account_risk_percent
                self.logger.info('<<Account Info>>')
                if self.margin_used > 0:
                    self.logger.info(f'Cash : {self.margin_used}')
                else:
                    self.logger.info(f'Margin Used : {self.margin_used}')
                try:
                    keys = list(self.universe['dividend_stocks'].keys())
                    self.logger.info(f'Dividend Stocks Buying Power : {self.total_free_margin * self.dividend_stocks_percent}')
                    for key in keys:
                        available_funds = (self.total_free_margin * self.dividend_stocks_percent * self.sector_funds_weight[key])
                        self.sector_funds_available['dividend_stocks'][key] += round(available_funds, 2) 
                        self.total_sector_funds['dividend_stocks'][key] += round(available_funds, 2)

                except Exception as ex:
                    self.logger.error(traceback.format_exc())
                    return False
    
            except Exception as ex:
                self.logger.error(traceback.format_exc())
                return False
            
            ##############################################################################
            ###################              Growth Stocks            ####################
            ##############################################################################
            try:
                sectors = list(self.universe['growth_stocks'].keys())
                for sector in sectors:
                    symbols_list = self.universe['growth_stocks'][sector]
                    for stock_info in symbols_list:
                        if isinstance(stock_info, dict):
                            symbol = stock_info['Symbol']
                            intrinsic_value = stock_info['Intrinsic Value']
                            ex_dividend_date = stock_info['Ex Dividend Date']
                        else:
                            symbol = stock_info
                            intrinsic_value = 'None'
                            ex_dividend_date = 'None'

                        if symbol in self.symbols:
                            #Add intrinsic value to active portfolio positions.
                            if isinstance(self.portfolio, dict):
                                self.portfolio[symbol]['intrinsic_value'] = intrinsic_value
                                self.portfolio[symbol]['ex_dividend_date'] = ex_dividend_date
                            try:
                                equity = float(self.portfolio[symbol]['equity'])
                                self.sector_funds_available['growth_stocks'][sector] -= round(equity, 2)
                                if symbol in list(self.pending_orders.keys()) and self.pending_orders[symbol]['side'] == 'buy':
                                    equity = self.pending_orders[symbol]['price'] * self.pending_orders[symbol]['quantity']
                                    self.sector_funds_available['growth_stocks'][sector] -= round(equity, 2)
                                        
                            except:
                                self.logger.error(traceback.format_exc())
                                return False

                self.total_portfolio_value = (self.total_market_value + self.total_buying_power)
                self.logger.info(f'Growth Stocks Buying Power : {self.total_free_margin * self.growth_stocks_percent}\n')
                try:
                    keys = list(self.universe['growth_stocks'].keys())
                    for key in keys:
                        available_funds = (self.total_free_margin * self.growth_stocks_percent * self.sector_funds_weight[key])
                        self.sector_funds_available['growth_stocks'][key] += round(available_funds, 2)
                        self.total_sector_funds['growth_stocks'][key] = round(available_funds, 2)
                except:
                    self.logger.error(traceback.format_exc())
                    return False
            except:
                self.logger.error(traceback.format_exc())
                return False

        return True

    def get_sector_performance(self, url):
        keys = 'None'
        alphavantage = 'None'
        try:
            alphavantage = requests.get(url).json()
            keys = list(alphavantage.keys())
        
            if 'Meta Data' in keys:
                return alphavantage
            else:
                if len(keys) > 0:
                    alphavantage = str(alphavantage[keys[0]])
                raise Exception(alphavantage)

        except Exception as ex:
            self.logger.error(traceback.format_exc())
            retry_count = 1
            while retry_count < 3:
                if 'Invalid API call' in alphavantage:
                    return -1
                else:
                    self.logger.error('Server Error! will retry in 60 sec...')
                    time.sleep(60)
                    alphavantage = requests.get(url).json()
                    keys = list(alphavantage.keys())
                    retry_count +=1
        
                    if 'Meta Data' in keys:
                        return alphavantage
                return 0

    def json_to_table(self, data):
        try:
            if isinstance(data, dict):
                _table = list()
                column_names = ['Date', 'Rank', 'Sector', 'Performance']
                df = 'None'
                table = list()
                sector = list()
                performance = list()
                table_names = list(data.keys())
                refresh_date = 'None'
                for x in range(len(table_names)):
                    table_name = table_names[x].split(':')
                    fields = data[table_names[x]]
                    column = list(fields.keys())
                    rows = list(fields.values())
                    #Strip percentage sign from data
                    for y in range(len(rows)):
                        rows[y] = rows[y].strip('%')

                    if 'Meta Data' in table_name:
                        refresh_date = rows[1][-10:]
                    else:
                        table_name = table_name[1].strip(' \t\n')
                        sectors = list(column)
                        performance = list(rows)
                        column.insert(0, table_name)
                        rows.insert(0, table_name)
                        column.insert(0, refresh_date)
                        rows.insert(0, refresh_date)
                        date = list()
                        rank = list()
                        for x in range(len(sectors)):
                            date.append(column[0])
                            rank.append(column[1])

                        table.append(pd.DataFrame({'Date':date, 'Rank':rank, 'Sector':sectors, 'Performance':performance}))

                _table = table
            else:
                self.logger.info('Invalid Datatype! JSON object expected!')
                    
        except Exception as ex:
            self.logger.error(traceback.format_exc())

        finally:
            return _table

    def calculate_position_size(self, stock_universe, stock_sector, stock_price, stock_symbol):
        positions = dict()
        number_of_shares = 0
        rank = self.get_symbol_rank(universe=stock_universe, sector=stock_sector, symbol=stock_symbol)
        self.logger.info(f'{stock_symbol} is ranked #{rank} in {stock_sector} sector!\n')

        if self.sector_funds_available[stock_universe][stock_sector] < stock_price:
            number_of_shares, positions = self.reallocate_funds(universe=stock_universe, sector=stock_sector, stock_price=stock_price, stock_symbol=stock_symbol)
        else:
            max_equity = self.total_sector_funds[stock_universe][stock_sector] * self.max_position_size_percent
            equity = self.total_sector_funds[stock_universe][stock_sector] * self.position_size_percent
                                
            if equity > max_equity:
                equity = max_equity

            if equity > self.sector_funds_available[stock_universe][stock_sector]:
                equity = self.sector_funds_available[stock_universe][stock_sector]

            try:
                number_of_shares = equity / stock_price
                number_of_shares = int(number_of_shares)

                if number_of_shares < 1:
                    number_of_shares, positions = self.reallocate_funds(universe=stock_universe, sector=stock_sector, stock_price=stock_price, stock_symbol=stock_symbol)

            except Exception as ex:
                self.logger.error(traceback.format_exc())

        return (number_of_shares, positions)

    def update_market_cycle(self):
        """
        Proprietary Information :- 
        Data was removed, for more information please contact author at julianjoseph52@gmail.com
        """
        pass
        
    def search_buy_opportunities(self, universe, testing=False):
        interval = '60min'
        SAR_period = '60min'
        positions = dict()
        positions_added = 0
        number_of_shares = 0
        try:
            for sector in list(self.universe[universe].keys()):
                symbols_list = list(self.universe[universe][sector])
                if sector == 'General' : continue #ignore all symbols in General - manually trading only
                self.logger.info(f'Searching {sector} sector for buying opportunities...\n')
                for symbol_info in symbols_list:
                    if not isinstance(symbol_info, str):
                        symbol = symbol_info['Symbol']
                        rating = symbol_info['Rating']
                        intrinsic_value = symbol_info['Intrinsic Value']
                    else:
                        symbol = symbol_info
                        rating = 'None'
                        intrinsic_value = 'None'
                    if symbol not in self.symbols and symbol not in list(self.pending_orders.keys()):
                        self.logger.info(f'Evaluating Buy Opportunity for {symbol}\n')
                        price_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&outputsize=full&apikey=demo'
                        self.PRICE = self.perse_data(price_url)
                        self.RSI = self.get_indicator_value(self.PRICE, indicator='RSI')
                        self.SAR = self.get_indicator_value(self.PRICE, indicator='SAR')
                        try:
                            idx = len(self.RSI) -1
                            rsi = float(self.RSI[idx])
                            idx = len(self.SAR) -1
                            sar = float(self.SAR[idx])
                            price = self.robinhood.get_latest_price(symbol)
                            if len(price) > 0:
                                price = float(price[0])
                            else:
                                price = -1
                            try:
                                periods_ago = self.cross_periods_ago(parabolic_SAR_data=self.SAR, current_price=price)
                                self.logger.info(f'{symbol} SAR crossed {periods_ago} periods ago!\n')

                                if price > sar and rsi > 50 and periods_ago < self.periods_ago_limit and intrinsic_value != 'None' and intrinsic_value < self.intrinsic_value_limit:
                                    self.logger.info(f'<<New Opportunity Found>>\n')
                                    try:
                                        number_of_shares, updated_positions = self.calculate_position_size(stock_universe=universe, stock_sector=sector, stock_price=price, stock_symbol=symbol)
                                        for _symbol in updated_positions:
                                            _quantity = updated_positions[_symbol]
                                            if _symbol in list(positions.keys()):
                                                positions[_symbol] += _quantity
                                            else:
                                                positions[_symbol] = _quantity
                                    except:
                                        self.logger.error(traceback.format_exc())

                                    if number_of_shares > 0:
                                        positions_added += 1
                                        equity = number_of_shares * price
                                        self.sector_funds_available[universe][sector] -= equity
                                        if not testing:
                                            results = self.open_position(symbol=symbol, quantity=number_of_shares, price=price) 
                                            if isinstance(results, bool) and results:
                                                positions[symbol] = quantity
                                        else: 
                                            positions[symbol] = quantity
                                            self.logger.info(f'<< Bought {quantity} shares of {symbol} at ${price}! >>') 
                            except:
                                self.logger.error(traceback.format_exc())    
                        except:
                            self.logger.error(traceback.format_exc())
                            if symbol in self.server_error:
                                self.logger.error(f'Invalid Symbol Detected! : {symbol}')
                                title = 'Invalid Symbol Detected!'
                                text = f'Error retrieving data for {symbol} from server!'
                                html = asi_email.create_simple_html_message(title, text)
                                asi_email.send_html_message(plain_text=text, html_text=html)
                            else:
                                self.logger.error(f'Error retrieving data for {symbol} from server! will retry next cycle...')
                                self.server_error.append(symbol)
                        finally:
                            self.logger.info(f'<<Price>> : {round(price, 2)}')
                            self.logger.info(f'<<RSI>> : {round(rsi, 2)}')
                            self.logger.info(f'<<SAR>> : {round(sar, 2)}')
                            self.logger.info(f'{symbol} Evaluation Complete!\n')
                            self.evaluation_info.update({symbol:{'PRICE': self.PRICE, 'RSI': self.RSI, 'SAR': self.SAR}})
        except:
            self.logger.error(traceback.format_exc())

        return (positions_added, positions)

    def perse_data(self, url):
        df = 'None'
        keys = 'None'
        alphavantage = 'None'
        def read_data():
            while not isInternet_Connected():
                self.logger.error("Please check internet connection! retry in 30 sec...")
                time.sleep(30)
            try:
                alphavantage = dict(requests.get(url).json())
                keys = list(alphavantage.keys())
                if 'Meta Data' in keys:
                    meta_data, data = alphavantage[keys[0]], alphavantage[keys[1]]  
                    df = pd.DataFrame.from_dict(data, orient='index', dtype=float)
                    df.index.name = 'Date'
                    return df
                else:
                    if 'Error Message' in keys:
                        message = alphavantage['Error Message']
                        if 'Invalid API call' in message:
                            return -5
                        else:
                            self.logger.error(message)
                            return -1
                    else:
                        if isinstance(alphavantage, dict) and not alphavantage:
                            return -5
                        else:
                            return -1
            except:
                self.logger.error(traceback.format_exc())
                return -1
                
        retry_count = 0
        while retry_count < 3:
            results = read_data()
            if isinstance(results, int):
                if results == -1:
                    self.logger.error('Server Error! will retry in 60 sec...')
                    retry_count += 1
                    time.sleep(60)
                else: 
                    return results
            else:
                return results

    def get_indicator_value(self, dataset, indicator):
        if isinstance(dataset, dict) or isinstance(dataset, pd.DataFrame):
            keys = dataset.keys()
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
            try:
                high = dataset[high_key].dropna().values
                low = dataset[low_key].dropna().values
                close = dataset[close_key].dropna().values
                volume = dataset[volume_key].dropna().values

                if indicator == 'RSI':
                    _RSI = RSI(close, timeperiod=14)
                    return _RSI

                elif indicator == 'SAR':
                    _SAR = SAR(high=high, low=low, acceleration=0.01, maximum=0.1)
                    return _SAR
                else:
                    return 'Unsupported Indicator'
            except:
                self.logger.error(traceback.format_exc())
        else:
            self.logger.error(f"Invalid 'dataset' provided! {type(dataset)}")
            self.logger.error("Expected: 'dict' or 'DataFrame'")

    def cross_periods_ago(self, parabolic_SAR_data, current_price):
        idx = len(parabolic_SAR_data) - 1
        number_of_periods = 0
        trend = 'None'
        price = float(current_price)
        while idx > 0:
            if idx >= 0:
                sar = parabolic_SAR_data[idx]
                sar = float(sar)
                idx -= 1

            if trend == 'None':
                if price > sar:
                    trend = 'Up'
                else:
                    trend = 'Down'

            if trend == 'Up':
                if price > sar:
                    number_of_periods += 1
                    price = sar
                else:
                    return number_of_periods

            if trend == 'Down':
                if sar > price:
                    number_of_periods += 1
                    price = sar
                else:
                    return number_of_periods

        return number_of_periods

    def get_portfolio_beta(self):
        stock_beta = 0
        portfolio_beta = 0
        portfolio_info = dict()
        try:
            self.update_sector_funds()
            try:
                self.logger.info('Calculating Portfolio Beta...\n')
                for symbol in self.symbols:
                    equity = float(self.portfolio[symbol]['equity'])
                    portfolio_diversity = equity / self.total_market_value
                    portfolio_info[symbol] = {'Beta':1, 'equity':equity, 'portfolio_diversity':portfolio_diversity}

                sectors = list(self.universe['growth_stocks'].keys())
                for sector in sectors:
                    symbols_list = self.universe['growth_stocks'][sector]
                    for stock_info in symbols_list:
                        if isinstance(stock_info, dict):
                            symbol = stock_info['Symbol']
                            stock_beta = stock_info['Beta']
                        else:
                            symbol = stock_info
                            stock_beta = 1

                        if symbol in self.symbols:
                            portfolio_info[symbol]['Beta'] = stock_beta

                sectors = list(self.universe['dividend_stocks'].keys())
                for sector in sectors:
                    symbols_list = self.universe['dividend_stocks'][sector]
                    for stock_info in symbols_list:
                        if isinstance(stock_info, dict):
                            symbol = stock_info['Symbol']
                            stock_beta = stock_info['Beta']
                        else:
                            symbol = stock_info
                            stock_beta = 1

                        if symbol in self.symbols:
                            portfolio_info[symbol]['Beta'] = stock_beta

                for symbol in self.symbols:
                    if symbol == 'UVXY' : continue
                    portfolio_beta += (portfolio_info[symbol]['Beta'] * portfolio_info[symbol]['portfolio_diversity'])
            except:
                self.logger.error(traceback.format_exc())
        except:
            self.logger.error(traceback.format_exc())

        finally:
            return portfolio_beta

    def get_inverse_stock_qty(self):
        quantity = 0
        UVXY_BETA = 1.46
        inverse_weight = 3
        self.portfolio_beta = self.get_portfolio_beta()
        total_market_value = copy.deepcopy(self.total_market_value)
        try:
            price = self.robinhood.get_latest_price('UVXY')
            if len(price) > 0:
                price = float(price[0])
            else:
                price = -1
            if not 'UVXY' in self.symbols:
                self.inverse_equity = 0
                inverse_equity = total_market_value * self.portfolio_beta
                inverse_equity /= UVXY_BETA
                inverse_equity /= inverse_weight
                quantity = int(inverse_equity / price)
                self.required_equity = copy.deepcopy(inverse_equity)
            else:
                self.inverse_equity = float(self.portfolio['UVXY']['equity'])
                if 'UVXY' in list(self.pending_orders.keys()) and self.pending_orders['UVXY']['side'] == 'buy':
                    self.inverse_equity += self.pending_orders['UVXY']['quantity'] * self.pending_orders['UVXY']['price']

                total_market_value -= self.inverse_equity
                inverse_equity = total_market_value * self.portfolio_beta
                inverse_equity /= UVXY_BETA
                inverse_equity /= inverse_weight
                quantity = int(inverse_equity / price)
                self.required_equity = copy.deepcopy(inverse_equity)
        except:
            self.logger.error(traceback.format_exc())
        finally:
            return quantity

    def hedge_portfolio(self):
        self.logger.info('Checking Portfolio Risk Level...\n')
        self.inverse_stock_quantity = self.get_inverse_stock_qty()
        localtime = time.localtime(time.time())
        if localtime.tm_hour >= 10 and localtime.tm_hour <= 12:
            if self.all_sectors_positive and self.mark_down_phase:
                if self.inverse_equity < (self.required_equity * 0.45):
                    self.logger.warning("Hedging portfolio...")
                    equity = ((self.required_equity * 0.50) - self.inverse_equity)
                    price = self.robinhood.get_latest_price('UVXY')
                    if len(price) > 0:
                        price = float(price[0])
                    else:
                        price = -1

                    number_of_shares = int(equity / price)

                    if number_of_shares > 0:
                        equity = number_of_shares * price
                        self.sector_funds_available['growth_stocks']['General'] -= equity
                        self.open_position(symbol='UVXY', quantity=number_of_shares, price=price)
                    else:
                        self.logger.warning("Error calculating inverse stock quantity for 'search_10AM_opportunity'") 
                else:
                    self.logger.warning("Portfolio Hedge Successful!")

        if localtime.tm_hour >= 15 and localtime.tm_hour <= 17:
            #self.search_buy_opportunities(universe='dividend_stocks')
            if self.all_sectors_positive and self.mark_down_phase:
                if self.inverse_equity < (self.required_equity * 0.90):
                    self.logger.warning("Hedging portfolio...\n")
                    equity = (self.required_equity - self.inverse_equity)
                    price = self.robinhood.get_latest_price('UVXY')
                    if len(price) > 0:
                        price = float(price[0])
                    else:
                        price = -1

                    number_of_shares = int(equity / price)

                    if number_of_shares > 0:
                        equity = number_of_shares * price
                        self.sector_funds_available['growth_stocks']['General'] -= equity
                        self.open_position(symbol='UVXY', quantity=number_of_shares, price=price) 
                    else:
                        self.logger.warning("Error calculating inverse stock quantity for 'search_3PM_opportunity'")
                else:
                    self.logger.warning("Portfolio Hedge Successful!") 
    def run(self):
        start_time = 0
        interval = '60min'
        SAR_period = '60min'
        ignore_list = list()
        current_time = time.time()
        self.robinhood.cancel_all_open_orders()
        asctime = str(datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d')) #Time for log file.
        sector_url = 'https://www.alphavantage.co/query?function=SECTOR&apikey=demo'
        while not self.exit:
            #Create 60 minutes timer
            timer_minutes = 60
            time_now = time.time()
            duration_seconds = timer_minutes * 60
            localtime = time.localtime(time.time())
            stop_time = start_time + duration_seconds
            if time_now > stop_time:
                count = 0 #number of sectors with negative performance values
                start_time = time.time()
                stop_time = start_time + duration_seconds
                json = self.get_sector_performance(sector_url)
                sectors_performance = self.json_to_table(json)
                realtime_performance = sectors_performance[0]
                
                if isinstance(realtime_performance, pd.DataFrame):
                    size = len(realtime_performance.index)
                    for x in range(size):
                        record = realtime_performance.iloc[x]
                        _date = str(record.Date)
                        _rank = str(record.Rank)
                        _sector = str(record.Sector)
                        _performance = str(record.Performance)
                        
                        if is_negative_number(_performance):
                            count += 1

                    self.logger.info(f'{count} out of {size} sectors are negative!')

                    if count >= size:
                        self.all_sectors_negative = True
                    else:
                        self.all_sectors_negative = False

                    if count == 0:
                        self.all_sectors_positive = True
                    else:
                        self.all_sectors_positive = False
                try:
                    ################################################################
                    ############         Manage Active Positions        ############
                    ################################################################
                    self.update_market_cycle()
                    self.update_sector_funds()
                    self.unrecognized_symbols = list()
                    dividend_stocks_list = list()
                    growth_stocks_list = list()
                    ignore_list = list()
                    if isinstance(self.universe, dict):
                        #Create stock lists and ignore list
                        for sector in list(self.universe['growth_stocks'].keys()):
                            stocks = self.universe['growth_stocks'][sector]
                            for stock_info in stocks:
                                if isinstance(stock_info, dict):
                                    symbol = stock_info['Symbol']
                                    growth_stocks_list.append(symbol)

                        for sector in list(self.universe['dividend_stocks'].keys()):
                            stocks = self.universe['dividend_stocks'][sector]
                            for stock_info in stocks:
                                if isinstance(stock_info, dict):
                                    symbol = stock_info['Symbol']
                                    dividend_stocks_list.append(symbol)

                        ignore_list.extend(self.universe['dividend_stocks']['General'])
                        ignore_list.extend(self.universe['growth_stocks']['General'])
                        ignore_list = list(set(ignore_list))
                except:
                    self.logger.error(traceback.format_exc())

                for symbol in self.symbols:
                    self.logger.info(f'Evaluating {symbol} Position...\n')
                    price_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&outputsize=full&apikey=demo'
                    self.PRICE = self.perse_data(price_url) 
                    self.RSI = self.get_indicator_value(self.PRICE, indicator='RSI')
                    self.SAR = self.get_indicator_value(self.PRICE, indicator='SAR')
                    try:
                        idx = len(self.RSI) -1
                        rsi = float(self.RSI[idx])
                        idx = len(self.SAR) -1
                        sar = float(self.SAR[idx])
                        try:
                            intrinsic_value = 'None'
                            ex_dividend_date = 'None'
                            stock_info = self.portfolio[symbol]
                            price = float(stock_info['price'])
                            percent_change = float(stock_info['percent_change'])
                            average_cost = float(stock_info['average_buy_price'])
                            try:
                                intrinsic_value = stock_info['intrinsic_value']
                                ex_dividend_date = stock_info['ex_dividend_date']
                            except:
                                if symbol not in ignore_list:
                                    self.logger.warning(f"{symbol} is Not in Trading Universe! Please add symbol to 'General' trading list!")
                                    self.unrecognized_symbols.append(symbol)
                            try:
                                quantity = stock_info['quantity']
                                if '.' in quantity:
                                    quantity = stock_info['quantity'].split('.')
                                    quantity = int(quantity[0])
                                else:
                                    quantity = stock_info['quantity']
                                    quantity = int(quantity)
                            except:
                                self.logger.error(traceback.format_exc()) 

                            if self.exit_positions and symbol not in ignore_list and symbol not in dividend_stocks_list:
                                self.logger.info(f"Exiting {symbol} position...")
                                if percent_change > self.percent_change_limit:
                                    self.close_position(symbol=symbol, quantity=quantity, price=price)
                                else:
                                    self.logger.warning(f"{symbol} is trading bellow StopLoss Limit!")

                            if price < sar and rsi < 50 and symbol not in ignore_list:
                                if isinstance(intrinsic_value, float):
                                    if intrinsic_value > self.max_intrinsic_value:
                                        self.logger.info(f"{symbol} is Overvalued...")
                                        self.close_position(symbol=symbol, quantity=quantity, price=price)
                                    else:
                                        self.logger.warning(f"{symbol} is in a temporary downtrend!")
                                else:
                                    if price > average_cost:
                                        self.close_position(symbol=symbol, quantity=quantity, price=price)
                                    else:
                                        self.logger.warning(f"{symbol} is in a downtrend and trading bellow average cost!")
                        except:
                            self.logger.error(traceback.format_exc())

                        finally:
                            self.logger.info(f'<<Price>> : {round(price, 2)}')
                            self.logger.info(f'<<RSI>> : {round(rsi, 2)}')
                            self.logger.info(f'<<SAR>> : {round(sar, 2)}')
                            self.logger.info(f'{symbol} Evaluation Complete!\n')
                            self.evaluation_info.update({symbol:{'PRICE': self.PRICE, 'RSI': self.RSI, 'SAR': self.SAR}})
                    except:
                        self.logger.error(traceback.format_exc())

                self.logger.info('<<Portfolio Evaluation Completed!>>\n\n')
                self.inverse_stock_quantity = self.get_inverse_stock_qty()
                self.logger.info(f"Portfolio Beta : {round(self.portfolio_beta, 2)}")
                self.logger.info(f"Current Portfolio Hedge : ${round(self.inverse_equity, 2)}")
                self.logger.info(f"Required Portfolio Hedge : ${round(self.required_equity, 2)}")
                self.logger.info(f"Market Cycle : {self.market_cycle}\n")
                self.screen_lock.release() 
                time.sleep(10)

                ###############################################################
                ###########         Manage Trading Universe        ############
                ###############################################################
                self.screen_lock.acquire() 
                positions_removed = 0
                positions_added = 0
                positions = dict()

                if isinstance(self.unrecognized_symbols, list) and len(self.unrecognized_symbols) > 0:
                    positions_removed, positions = self.rebalance_portfolio(universe='growth_stocks')

                if isinstance(self.universe, dict):
                    if localtime.tm_hour >= 10 and localtime.tm_hour <= 12 and not self.search_10AM_opportunity:
                        self.search_10AM_opportunity = True
                        self.logger.info('Scanning for Investing Opportunities...\n')
                        positions_added, positions = self.search_buy_opportunities(universe='dividend_stocks')
                        
                        if positions_added > 0:
                            positions_removed, positions = self.rebalance_portfolio(universe='dividend_stocks')
                        
                        if not self.sell_only:
                            self.logger.info('Scanning for Trading Opportunities...\n')
                            positions_added, positions = self.search_buy_opportunities(universe='growth_stocks') 
                            
                            if positions_added > 0:
                                positions_removed, positions = self.rebalance_portfolio(universe='growth_stocks')

                    if localtime.tm_hour >= 15 and localtime.tm_hour <= 17 and not self.search_3PM_opportunity:
                        self.search_3PM_opportunity = True
                        self.logger.info('Scanning for Investing Opportunities...\n')
                        positions_added, positions = self.search_buy_opportunities(universe='dividend_stocks')
                        
                        if positions_added > 0:
                            positions_removed, positions = self.rebalance_portfolio(universe='dividend_stocks')
                        
                        if not self.sell_only:
                            self.logger.info('Scanning for Trading Opportunities...\n')
                            positions_added, positions = self.search_buy_opportunities(universe='growth_stocks') 
                            
                            if positions_added > 0:
                                positions_removed, positions = self.rebalance_portfolio(universe='growth_stocks')
                else:
                    self.logger.error('Error importing trading universe!')

                total_holdings = len(self.symbols)
                self.logger.info('<<Portfolio is Up to Date!>>\n')
                self.logger.info(f'{positions_added} Positions Added!')
                self.logger.info(f'{positions_removed} Positions Removed!')
                self.logger.info(f'Total Current Holdings : {total_holdings} Positions')
                self.logger.info(f'Current Positions : {self.symbols}\n')
                self.save_stock_portfolio_state()

            self.hedge_portfolio()
            self.screen_lock.release()
            time.sleep(30)
                
    
#####################################################
##########            Getters            ############
#####################################################
    @property
    def portfolio_info(self):
        return self.evaluation_info

    @property
    def stop(self):
        return self.exit   

    @property
    def update_logger(self):
        return self.logger

    @property
    def _sell_only(self):
        return self.sell_only

    @property
    def update_universe(self):
        return self.universe

    @property
    def update_total_sector_funds(self):
        return self.total_sector_funds

    @property
    def update_sector_funds_available(self):
        return self.sector_funds_available

    @property
    def update_portfolio(self):
        return self.portfolio 

#####################################################
##########            Setters            ############
#####################################################
    @portfolio_info.setter
    def portfolio_info(self, info):
        self.evaluation_info = info

    @_sell_only.setter
    def _sell_only(self, info):
        self.sell_only = info

    @update_logger.setter
    def update_logger(self, info):
        self.logger = info

    @update_portfolio.setter
    def update_portfolio(self, info):
        self.portfolio = info

    @update_universe.setter
    def update_universe(self, info):
        self.universe = info

    @update_total_sector_funds.setter
    def update_total_sector_funds(self, info):
        self.total_sector_funds = info

    @update_sector_funds_available.setter
    def update_sector_funds_available(self, info):
        self.sector_funds_available = info

    @stop.setter
    def stop(self, state):
        self.save_stock_portfolio_state()
        self.search_3PM_opportunity = False
        self.search_10AM_opportunity = False
        self.exit = state
    
def start_ASI(duration=525600):
    """
    duration (interger): number of minutes to run ASI before self termination
    default duration : 1 year / 525600 minutes
    """
    duration_seconds = duration * 60
    system_timer = time.time()
    system_start_time = time.time()
    system_stop_time = system_start_time + duration_seconds
    screen_lock = Semaphore(value=1)
    manage_portfolio_active = False
    update_database_active = False

    MON, TUE, WED, THU, FRI, SAT, SUN = range(7) #Enumerate days of the week

    asctime = str(datetime.datetime.fromtimestamp(system_start_time).strftime('%Y-%m-%d'))

    #Setup logging to file
    logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s %(name)-10s %(levelname)-8s %(message)s',
                   datefmt='%Y-%m-%d %H:%M',
                   filename=f'logs/{asctime} ASI log.log',
                   filemode='a')

    #Define a handler to write INFO messages or higher to system output
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    #Setup output format for console.
    formatter = logging.Formatter('%(name)-27s : %(levelname)-8s %(message)s')
    console.setFormatter(formatter)

    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    #setup loggers to debug program
    logger_main = logging.getLogger('ASI.Main Thread')
    system_logs = {'logger':logging}

    print()
    logger_main.info("Current Time : " + str(datetime.datetime.fromtimestamp(system_start_time).strftime('%Y-%m-%d %H:%M:%S')))
    logger_main.info("System Stop Time : " + str(datetime.datetime.fromtimestamp(system_stop_time).strftime('%Y-%m-%d %H:%M:%S')))
    logger_main.info('Artificial Superintelligence is active...\n')
 
    portfolio = 'None'
    database = 'None'
    #portfolio = Manage_Stocks_Portfolio(thread_lock=screen_lock, logs=system_logs) 
    #database = Manage_Stocks_Database(thread_lock=screen_lock, logs=system_logs)

    while True:
        try:  
            localtime = time.localtime(time.time())
            #Set market hours
            if localtime.tm_hour >= 9 and localtime.tm_hour <= 16 and localtime.tm_wday >= MON and localtime.tm_wday <= FRI:
                if not manage_portfolio_active:
                    portfolio = Manage_Stocks_Portfolio(thread_lock=screen_lock, logs=system_logs) 
                    manage_portfolio_active = True
                    update_database_active = False
                    if not isinstance(database, str):
                        database.stop = True
                        pass
            else:
                if not update_database_active:
                    database = Manage_Stocks_Database(thread_lock=screen_lock, logs=system_logs)
                    update_database_active = True
                    manage_portfolio_active = False
                    if not isinstance(portfolio, str):
                        portfolio.stop = True
                        pass
            #logger_main.info('Main loop running...')
            if not isinstance(portfolio, str):
                info = portfolio.portfolio_info
                show_portfolio_evaluations(info)

            time.sleep(60)
            if time.time() > system_stop_time:
                print()
                logger_main.warning('ASI shutting down...')
                break
        except KeyboardInterrupt:
            try:
                print()
                logger_main.warning('Manual Override! ASI shutting down...')
                if not isinstance(portfolio, str):
                    portfolio.stop = True

                if not isinstance(database, str):
                    database.stop = True

            except Exception as ex:
                if not isinstance(ex, NameError):
                    logger_main.error(traceback.format_exc()) 
            #Exit main loop
            break

if __name__ == '__main__':
    start_ASI()