import unittest
import os
import pandas as pd

class TestSortGS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        '''Run once before all tests'''
        os.system("sortgs 'machine learning' --debug --nresults 10 --endyear 2022")
        cls.df_top_10_cli = pd.read_csv('machine_learning.csv')

        os.system("sortgs 'machine learning' --debug --nresults 10 --endyear 2022 --sortby 'cit/year'")
        cls.df_top_sorted_cit_per_year_cli = pd.read_csv('machine_learning.csv')

    def test_get_10_results_cli(self):
        self.assertEqual(len(self.df_top_10_cli), 10)

    def test_is_sorted_by_citations(self):
        df = self.df_top_10_cli
        top_citations = list(df.Citations.values[:5])
        self.assertEqual(top_citations, [3166, 2853, 2416, 948, 830])

    def test_top_result_cli(self):
        df = self.df_top_10_cli
        top_author = str(df.Author.values[0]).strip()
        top_citation = int(df.Citations.values[0])
        top_cit_per_year = int(df['cit/year'].values[0])
        top_results = [top_author, top_citation, top_cit_per_year]
        self.assertEqual(top_results, ['S Shalev-Shwartz, S Ben-David', 3166, 352])

    def test_cit_per_year_sorted(self):
        df = self.df_top_sorted_cit_per_year_cli
        top_cit_per_year = list(df['cit/year'].values[:5])
        self.assertEqual(top_cit_per_year, [571, 352, 302, 85, 79])

    def test_csv_exists(self):
        self.assertTrue(os.path.exists('machine_learning.csv'))

    def test_cli_cit_per_year_sorted(self):
        df = self.df_top_sorted_cit_per_year_cli
        top_citations = list(df.Citations.values[:5])
        top_cit_per_year = list(df['cit/year'].values[:5])
        
        # Convert np.int64 values to Python int
        top_citations = [int(c) for c in top_citations]
        top_cit_per_year = [int(c) for c in top_cit_per_year]

        top_results = [top_citations, top_cit_per_year]
        self.assertEqual(top_results, [
            [2853, 3166, 2416, 598, 948],
            [571, 352, 302, 85, 79]
        ])
    
    def test_top_5_authors(self):
        '''Check if the top 5 authors match the expected authors.'''
        df = self.df_top_10_cli
        top_5_authors = list(df.Author.values[:5])
        expected_authors = [
            'S Shalev-Shwartz, S Ben-David', 
            'M Mohri, A Rostamizadeh, A Talwalkar', 
            'MI Jordan, TM Mitchell', 
            'C Sammut, GI Webb', 
            'P Langley'
        ]
        self.assertEqual(top_5_authors, expected_authors)

    def test_top_5_titles(self):
        '''Check if the top 5 titles match the expected titles.'''
        df = self.df_top_10_cli
        top_5_titles = list(df.Title.values[:5])
        expected_titles = [
            'Understanding machine learning: From theory to algorithms',
            'Foundations of machine learning',
            'Machine learning: Trends, perspectives, and prospects',
            'Encyclopedia of machine learning',
            'Elements of machine learning'
        ]
        self.assertEqual(top_5_titles, expected_titles)

if __name__=='__main__':
    unittest.main()