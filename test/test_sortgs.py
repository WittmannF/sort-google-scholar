import unittest
from unittest.mock import patch
import sortgs
import os
import pandas as pd

class TestSortGS(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        '''run once before all tests'''
        os.system("python sortgs.py --debug --kw 'machine learning' --nresults 10")
        self.df_top_10=pd.read_csv('machine_learning.csv')

        os.system("python sortgs.py --debug --kw 'machine learning' --nresults 20")
        self.df_top_20=pd.read_csv('machine_learning.csv')

        os.system("python sortgs.py --debug --kw 'machine learning' --nresults 20 --sortby 'cit/year'")
        self.df_top_sorted_cit_per_year=pd.read_csv('machine_learning.csv')
    
    def test_get_10_results(self):
        self.assertEqual(len(self.df_top_10), 10)
    
    def test_get_20_results(self):
        self.assertEqual(len(self.df_top_20), 20)
    
    def test_is_sorted(self):
        df=self.df_top_20
        top_citations=list(df.Citations.values[:5])
        self.assertEqual(top_citations, [49230, 8603, 3166, 3069, 2853])
    
    def test_top_result(self):
        df=self.df_top_20
        top_author = str(df.Author.values[0])
        top_citation = int(df.Citations.values[0])
        top_cit_per_year = int(df['cit/year'].values[0])
        top_results = [top_author, top_citation, top_cit_per_year]
        self.assertEqual(top_results, [' Bishop', 49230, 2896])

    def test_cit_per_year_sorted(self):
        df=self.df_top_sorted_cit_per_year
        top_citations=list(df.Citations.values[:5])
        top_cit_per_year = list(df['cit/year'].values[:5])
        top_results = [top_citations, top_cit_per_year]
        self.assertEqual(top_results, [[49230, 8603, 2853, 3166, 2416],
                                        [2896, 782, 571, 352, 302]])

    def test_csv_exists(self):
        os.system("python sortgs.py --debug --kw 'machine learning' --nresults 10")
        self.assertTrue(os.path.exists('machine_learning.csv'))


if __name__=='__main__':
    unittest.main()