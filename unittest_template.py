import test_module
import unittest
from unittest import TestCase

class TestModule(TestCase):
	@classmethod
	def setUpClass(cls):
		pass

	@classmethod
	def tearDownClass(cls):
		pass

	def setUp(self):
		pass

	def tearDown(self):
		pass

if __name__ == '__main__':
	unittest.main()