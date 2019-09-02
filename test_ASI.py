import os
import ASI
import time
import logging
import datetime
import unittest
from threading import *
from unittest import TestCase
root_dir = os.getcwd()#Get current working directory

class test_is_negative_number(TestCase):
	"""Test ASI.py : is_negative_number()"""
	def test_positive_num_less_than_zero(self):
		value = 0.00456
		results = ASI.is_negative_number(value)
		self.assertFalse(results, 'incorrect results for positive value less than zero')

	def test_negative_num_less_than_zero(self):
		value = -0.05637
		results = ASI.is_negative_number(value)
		self.assertTrue(results, 'incorrect results for negative value less than zero')

	def test_negative_integer(self):
		value = -13
		results = ASI.is_negative_number(value)
		self.assertTrue(results, 'incorrect results for negative integer value')

	def test_positive_integer(self):
		value = 48
		results = ASI.is_negative_number(value)
		self.assertFalse(results, 'incorrect results for positive integer value')

class Test_Manage_Stocks_Portfolio(TestCase):
	@classmethod
	def setUpClass(cls):
		time_now = time.time()
		screen_lock = Semaphore(value=1)
		asctime = str(datetime.datetime.fromtimestamp(time_now).strftime('%Y-%m-%d'))

		#Setup logging to file
		logging.basicConfig(level=logging.INFO,
							format='%(asctime)s %(name)-10s %(levelname)-8s %(message)s',
							datefmt='%Y-%m-%d %H:%M',
							filename=f'{asctime} test_ASI log.log',
							filemode='a')

		#Define a handler to write INFO messages or higher to system output
		console = logging.StreamHandler()
		console.setLevel(logging.INFO)

		#Setup output format for console.
		formatter = logging.Formatter('%(name)-27s : %(levelname)-8s %(message)s')
		console.setFormatter(formatter)

		# add the handler to the root logger
		logging.getLogger('').addHandler(console)
		system_logs = {'logger':logging}
		cls.logs = system_logs

		cls.manage_portfolio = ASI.Manage_Stocks_Portfolio(thread_lock=screen_lock, logs=system_logs, testing=True)
		# Import Testing Data
		file_path = f'{root_dir}/test_database/'
		cls.sector_funds_available = ASI.read_from_File(file_path + 'sector_funds_available.txt')
		cls.total_sector_funds = ASI.read_from_File(file_path + 'total_sector_funds.txt')
		
		file_path = f'{root_dir}/test_database/universe/'
		growth_stocks = ASI.read_from_File(file_path + 'growth_stocks_universe.txt')
		dividend_stocks = ASI.read_from_File(file_path + 'dividend_stocks_universe.txt')
		universe = dict()
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
			cls.universe = universe
		else:
			universe.update({'dividend_stocks' : dict()})
			universe.update({'growth_stocks' : dict()})
			universe['dividend_stocks'].update({'General': ['UVXY', 'SPXL']})
			universe['growth_stocks'].update({'General': ['UVXY', 'SPXL']})
			print('Error importing trading universe!')
			cls.universe = universe

	@classmethod
	def tearDownClass(cls):
		pass

	def setUp(self):
		file_name = f'{root_dir}/test_database/current_holdings.txt'
		self.sell_only = False
		self.portfolio = ASI.read_from_File(file_name)
		self.logger = self.logs['logger'].getLogger('ASI.Test_Manage_Stocks_Portfolio')
		self.manage_portfolio.update_sector_funds_available = self.sector_funds_available
		self.manage_portfolio.update_total_sector_funds = self.total_sector_funds
		self.manage_portfolio.update_portfolio = self.portfolio
		self.manage_portfolio.update_universe = self.universe
		self.manage_portfolio.update_logger = self.logger
		self.manage_portfolio._sell_only = self.sell_only

	def tearDown(self):
		pass

	def test_reallocate_funds(self):
		self.logger.info("Testing Reallocate Funds...")
		# Test better trading opportunity
		number_of_shares, positions = self.manage_portfolio.reallocate_funds(universe='dividend_stocks', sector='Real Estate', stock_price=18.65, stock_symbol='MPW', testing=True)
		self.assertEqual(number_of_shares, 1)
		self.assertEqual(positions['ADC'], -7)
		self.assertEqual(positions['HTA'], -5)
		self.assertEqual(positions['LOAN'], -2)
		self.assertEqual(len(positions), 3)
	
		# Test worst trading opportunity
		number_of_shares, positions = self.manage_portfolio.reallocate_funds(universe='dividend_stocks', sector='Real Estate', stock_price=264.70, stock_symbol='PSA', testing=True)
		self.assertEqual(number_of_shares, 0)
		self.assertEqual(len(positions), 0)

	def test_rebalance_portfolio(self):
		self.logger.info("Testing Rebalance Portfolio...")
		positions_removed, positions = self.manage_portfolio.rebalance_portfolio(universe='growth_stocks', testing=True)
		if self.sell_only:
			# Real Estate Stocks
			self.assertEqual(positions_removed, 0)
			self.assertEqual(positions['ADC'], -14)
		else:
			# Real Estate Stocks
			self.assertEqual(positions_removed, 0)
			self.assertEqual(positions['ADC'], -14)
			self.assertEqual(positions['MPW'], 7)
			self.assertEqual(positions['HTA'], 6)
			self.assertEqual(positions['GOOD'], 13)
			self.assertEqual(positions['NYMT'], 50)
			self.assertEqual(positions['STAG'], 1)
			# Technology Stocks
			self.assertEqual(positions['STM'], -12)
			self.assertEqual(positions['WSO'], -1)
			self.assertEqual(positions['INTC'], -2)
			self.assertEqual(positions['MSFT'], -1)
			self.assertEqual(positions['DCMYY'], -1)
			self.assertEqual(positions['OTEX'], -1)
			self.assertEqual(positions['INTU'], -1)
			self.assertEqual(positions['GSB'], -9)

if __name__ == '__main__':
	unittest.main()