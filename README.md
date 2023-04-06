## Sort Google Scholar by the Number of Citations V2.0b
This Python code ranks publications data from Google Scholar by the number 
of citations. It is useful for finding relevant papers in a specific field. 

The data acquired from Google Scholar is Title, Citations, Links and Rank. A new
columns with the number of citations per year is also included.
The example of the code will look for the top 100 papers related to the keyword, 
and rank them by the number of citations. This keyword can eiter be included in 
the command line terminal (`$python sortgs.py --kw 'my keyword'`) or edited in 
the original file.
As output, a .csv file will be returned with the name of the chosen keyword
ranked by the number of citations.

### UPDATES
- Try running the code using Google Colab -> [<img src="https://colab.research.google.com/assets/colab-badge.svg" align="center">](https://colab.research.google.com/github/WittmannF/sort-google-scholar/blob/master/Test_sortgs_py_on_Colab.ipynb)
    - No install requirements! Limitations: Can't handle robot checking, so use it carefully.
- Command line arguments. Ex: `$python sortgs.py --kw "deep learning"` (results saved in `deep_learning.csv`)
- Handling robot checking with selenium.
    - OBS: You might be asked to manually solve the first captcha for retrieving the content of the pages

### Misc
If this project was helpful to you in any way, feel free to buy me a cup of coffee :)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=QAQ4YJFQVXLMA&source=url)

For a feedback, send me an email: fernando [dot] wittmann [at] gmail [dot] com


### Usage of `sortgs.py`
```
usage: sortgs.py [-h] [--kw KEYWORD] [--sortby SORTBY] [--nresults NRESULTS]
                 [--csvpath CSVPATH] [--notsavecsv] [--plotresults]
                 [--startyear STARTYEAR] [--endyear ENDYEAR]

Example: $python sortgs.py --kw 'deep learning'

optional arguments:
  -h, --help            show this help message and exit
  --kw KEYWORD          Keyword to be searched. Default is 'machine learning'
                        Use double quote followed by simple quote to search 
			for an exact keyword. Example: "'exact keyword'"
  --sortby SORTBY       Column to be sorted by. Default is by the columns
                        "Citations", i.e., it will be sorted by the number of
                        citations. If you want to sort by citations per year,
                        use --sortby "cit/year"
  --nresults NRESULTS   Number of articles to search on Google Scholar.
                        Default is 100. (carefull with robot checking if value
                        is too high)
  --csvpath CSVPATH     Path to save the exported csv file. By default it is
                        the current folder
  --notsavecsv          By default results are going to be exported to a csv
                        file. Select this option to just print results but not
                        store them
  --plotresults         Use this flag in order to plot the results with the
                        original rank in the x-axis and the number of citaions
                        in the y-axis. Default is False
  --startyear STARTYEAR
                        Start year when searching. Default is None
  --endyear ENDYEAR     End year when searching. Default is current year
```

### Example
The following code will search for the top 100 results, rank by number of citations and save as a .csv file (same name of the keyword):
```
$python sortgs.py --kw "machine learning"
```

Sorted by number of citations per year (**HIGHLY RECOMMENDED**):
```
$python sortgs.py --kw "machine learning" --sortby "cit/year"
```

From 2005 to 2015:
```
$python sortgs.py --kw "machine learning" --startyear 2005 --endyear 2015
```

Search for an exact keywork:
```
$python sortgs.py --kw "'machine learning'"
```

Save results under a subfolder called 'examples'
```
$python sortgs.py --kw 'neural networks' --csvpath './examples/'
```

You can also add multiple keywords by fencing them with a single quote:
```
$python sortgs.py --kw '"deep learning" OR "neural networks" OR "machine learning"' --sortby "cit/year"
```

Example of output while running:
```
Loading next 10 results
Robot checking detected, handling with selenium (if installed)
Loading...
Solve captcha manually and press enter here to continue...
year not found, appending 0
Loading next 20 results
Robot checking detected, handling with selenium (if installed)
Loading next 30 results
Robot checking detected, handling with selenium (if installed)
Loading next 40 results
```

### Installation
SortGS is not available (yet) on PyPa. The most straight foward way to use it is the following:
1. Install Python 3 and its dependencies from **Requirements** (suggestion: use Ananconda https://www.anaconda.com/distribution/)
2. Download the repository. Two ways to do this:
    - Use the command `git clone https://github.com/WittmannF/sort-google-scholar.git` in your terminal (if linux/MAC) or CMD (if windows)
    - Or download using this link: https://github.com/WittmannF/sort-google-scholar/archive/master.zip and unzip
3. Open the folder of sortgs on your terminal (if linux/MAC) or CMD (if windows)
4. Use the command `python sortgs.py --kw "your keyword"` (replace "your keyword" to any keyword that you'd like to search)
5. A CSV file with the name `your_keyword.csv` should be created. 

If those steps are too complicated for you, send me an email with a list of keyworks that you'd like them ranked to: fernando [dot] wittmann [at] gmail [dot] com

### Requirements
If you install anaconda, all of those requirements (except selenium) are going to be met:
- Python 2.7 or Python 3
- Install from the requirements file: `pip install -r requirements.txt`

Highly suggested, if having problems with robot checking:
- ChromeDriver: http://chromedriver.chromium.org/
    - After downloading chromedriver, rename it to `chromedriver` and add it in a folder accessible by the PATH (Example: your python directory. Mine is at `/Users/.../anaconda/bin/`)

### Contributing
In order to make contributions, all of the tests must be passed. In order to test the code, we will be using the DEBUG mode which is going to use a URL from web archive. Please make sure to save the URL you want to test on web archive in case it is different from the one I already saved. By default it only works in debug mode when using the keywords 'machine learning'. There are 6 tests and all of them are testing different aspects that should match when using SortGS. In order to run the test cases, just run:
```
$python -m unittest
```

### LICENSE
- MIT


#### Citation
This code was originally developed for my [MS Dissertation](http://repositorio.unicamp.br/jspui/handle/REPOSIP/330610). For referencing this tool, you can use the following:

```
WITTMANN, Fernando Marcos. Optimization applied to residential non-intrusive load monitoring. 2017. 
Dissertation (Masters) - University of Campinas, School of Electrical and Computer Engineering, Campinas, SP. 
Available in: <http://www.repositorio.unicamp.br/handle/REPOSIP/330610>.
```
