import unittest
import Utils

class TestUtils(unittest.TestCase):
	def testLoad_variables_fromini(self):
		variables = Utils.load_variables_fromini()
		self.assertIsNotNone(variables)
		assert variables is not None

#unittest.main()