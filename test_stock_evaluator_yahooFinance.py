import os
import time
import math
import logging
import unittest
import datetime
import pandas as pd
from unittest import TestCase
from StockMarket import stock_evaluator_yahooFinance
ROOT_DIR = os.getcwd()

class TestStockExtractor(TestCase):
	@classmethod
	def setUpClass(cls):
		pass

	@classmethod
	def tearDownClass(cls):
		pass

	def setUp(self):
		time_now = time.time()
		asctime = str(datetime.datetime.fromtimestamp(time_now).strftime('%Y-%m-%d'))

		#Setup logging to file
		logging.basicConfig(level=logging.INFO,
							format='%(asctime)s %(name)-10s %(levelname)-8s %(message)s',
							datefmt='%Y-%m-%d %H:%M',
							filename=f'{asctime} test_yahooFinance log.log',
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

		self.file_path = f'{ROOT_DIR}/test_database'
		self.industries = ['Software - Infrastructure', 'REIT - Residential', 'REIT - Healthcare Facilities']
		self.top_growth_stocks_by_sector = {'Technology':{'Software - Infrastructure':[]},'Real Estate':{'REIT - Residential':[],'REIT - Healthcare Facilities':[]}}
		self.top_dividend_stocks_by_sector = {'Technology':{'Software - Infrastructure':[]},'Real Estate':{'REIT - Residential':[],'REIT - Healthcare Facilities':[]}}
		self.sectors = ['Technology', 'Real Estate', 'Financial Services', 'Consumer Cyclical']
		self.Evaluator = stock_evaluator_yahooFinance.StockExtractor(company_groups=self.industries, logs=system_logs)

	def tearDown(self):
		del self.sectors
		del self.Evaluator
		del self.file_path
		del self.industries
		del self.top_growth_stocks_by_sector
		del self.top_dividend_stocks_by_sector

	def test_evaluate_stock_poor_company(self):
		#Evaluate stock
		self.symbol = 'DX'
		self.sector = 'Real Estate'
		self.industry = 'REIT - Residential'
		self.stock_data = pd.read_csv(f"{self.file_path}/DX.csv", index_col=[0])
		self.Evaluator.evaluate_stock(self.symbol, testing=True)
		self.Evaluator.update_annual_performance(self.stock_data)
		self.Evaluator.update_TTM_performance(self.stock_data)
		self.Evaluator.update_intrinsic_value()
		self.evaluation = self.Evaluator.get_dividend_companies[self.industry][0]
		symbol = self.evaluation['Symbol']
		if isinstance(self.evaluation['Rating'], float):
			rating = math.floor(self.evaluation['Rating'])
		else:
			rating = False

		if isinstance(self.evaluation['Intrinsic Value'], float):
			intrinsic_value = math.floor(self.evaluation['Intrinsic Value'])
		else:
			intrinsic_value = False

		if isinstance(self.evaluation['Performance(Annual)'], float):
			annual_stock_performance = math.floor(self.evaluation['Performance(Annual)'])
		else:
			annual_stock_performance = False

		if isinstance(self.evaluation['Revenue Growth(Annual)'], float):
			annual_revenue_growth = math.floor(self.evaluation['Revenue Growth(Annual)'])
		else:
			annual_revenue_growth = False

		if isinstance(self.evaluation['TTM Stock Performance'], float):
			TTM_stock_performance = math.floor(self.evaluation['TTM Stock Performance'])
		else:
			TTM_stock_performance = False

		if isinstance(self.evaluation['TTM Revenue Growth'], float):
			TTM_revenue_growth = math.floor(self.evaluation['TTM Revenue Growth'])
		else:
			TTM_revenue_growth = False

		print(f"\n<<stock evaluation>> \n{self.evaluation}\n")

		self.assertEqual(symbol, self.symbol)
		self.assertTrue(intrinsic_value > 0)
		self.assertAlmostEqual(rating, math.floor(1299.711))
		self.assertAlmostEqual(TTM_revenue_growth, math.floor(-991.556))
		self.assertAlmostEqual(annual_revenue_growth, math.floor(14.968))
		self.assertAlmostEqual(TTM_stock_performance, math.floor(-17.007))
		self.assertAlmostEqual(annual_stock_performance, math.floor(-3.736))

	def test_evaluate_stock_strong_company(self):
		#Evaluate stock
		self.symbol = 'MSFT'
		self.sector = 'Technology'
		self.industry = 'Software - Infrastructure'
		self.stock_data = pd.read_csv(f"{self.file_path}/MSFT.csv", index_col=[0])
		self.Evaluator.evaluate_stock(self.symbol, testing=True)
		self.Evaluator.update_annual_performance(self.stock_data)
		self.Evaluator.update_TTM_performance(self.stock_data)
		self.Evaluator.update_intrinsic_value()
		self.evaluation = self.Evaluator.get_dividend_companies[self.industry][0]
		symbol = self.evaluation['Symbol']
		if isinstance(self.evaluation['Rating'], float):
			rating = math.floor(self.evaluation['Rating'])
		else:
			rating = False

		if isinstance(self.evaluation['Intrinsic Value'], float):
			intrinsic_value = math.floor(self.evaluation['Intrinsic Value'])
		else:
			intrinsic_value = False

		if isinstance(self.evaluation['Performance(Annual)'], float):
			annual_stock_performance = math.floor(self.evaluation['Performance(Annual)'])
		else:
			annual_stock_performance = False

		if isinstance(self.evaluation['Revenue Growth(Annual)'], float):
			annual_revenue_growth = math.floor(self.evaluation['Revenue Growth(Annual)'])
		else:
			annual_revenue_growth = False

		if isinstance(self.evaluation['TTM Stock Performance'], float):
			TTM_stock_performance = math.floor(self.evaluation['TTM Stock Performance'])
		else:
			TTM_stock_performance = False

		if isinstance(self.evaluation['TTM Revenue Growth'], float):
			TTM_revenue_growth = math.floor(self.evaluation['TTM Revenue Growth'])
		else:
			TTM_revenue_growth = False

		print(f"\n<<stock evaluation>> \n{self.evaluation}\n")

		self.assertEqual(symbol, self.symbol)
		self.assertTrue(intrinsic_value < 0)
		self.assertAlmostEqual(rating, math.floor(2827.997))
		self.assertAlmostEqual(TTM_revenue_growth, math.floor(54.126))
		self.assertAlmostEqual(annual_revenue_growth, math.floor(31.478))
		self.assertAlmostEqual(TTM_stock_performance, math.floor(24.541))
		self.assertAlmostEqual(annual_stock_performance, math.floor(58.706))

	def test_intrinsic_value(self):
		#Evaluate stock
		self.symbol = 'WELL'
		self.sector = 'Real Estate'
		self.industry = 'REIT - Healthcare Facilities'
		self.stock_data = pd.read_csv(f"{self.file_path}/WELL.csv", index_col=[0])
		self.Evaluator.evaluate_stock(self.symbol, testing=True)
		test_data = [[15, 5, 25, 5, True], [15, 5, 8, 5, False], [5, 15, 3, 18, False], [5, 15, 18, 3, True],
		[18, 9, 3, 15, False], [-15, -5, -25, -5, False], [-15, -5, -8, -5, False], [-5, -15, -3, -18, True],
		[-5, -15, -18, -3, False], [-18, -9, -3, -15, True], [15, -5, 25, -5, True], [-15, 5, -25, 5, False],
		[15, 5, 25, -5, True], [15, -5, 5, 5, False], [-15, 5, 30, 5, True], [15, 5, -10, 5, False]]

		count = 0
		fail_count = 0
		for test in test_data:
			greater_than_zero = test[4]
			self.Evaluator.set_evaluation_values(test)
			intrinsic_value = self.Evaluator.update_intrinsic_value()
			try:
				self.assertEqual(greater_than_zero, intrinsic_value > 0)
				print('Pass!')
				count += 1
			except:
				fail_count += 1
				print('Failed!')

			print(f"test data : {test}")
			print(f"intrinsic_value : {intrinsic_value}")
		
		print(f"Pass count : {count}")
		print(f"Fail count : {fail_count}")
		self.assertEqual(fail_count, 0)

if __name__ == '__main__':
	unittest.main()