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

### New Features
- Command line arguments. Ex: `$python sortgs.py --kw "deep learning"`
- Handling robot checking with selenium.
    - OBS: You might be asked to manually solve the first captcha for retrieving the content of the pages

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

Sorted by number of citations per year:
```
$python sortgs.py --kw "machine learning" --sortby "cit/year"
```

From 2005 to 2015:
```
$python sortgs.py --kw "machine learning" --startyear 2005 --endyear 2015
```

Save results under a subfolder called 'examples'
```
$ python sortgs.py --kw 'neural networks' --csvpath './examples/'
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

### Requirements
If you install anaconda, all of those requirements (except s) are going to be met:
- Python 2.7 or Python 3
- Requests: `pip install requests`
- Beautiful Soup: `pip install beautifulsoup4`
- Pandas: `pip install pandas`
- Matplotlib: `pip install matplotlib`

Highly suggested, if having problems with robot checking:
- Selenium: `pip install selenium`
- ChromeDriver: http://chromedriver.chromium.org/
    - After downloading chromedriver, rename it to `chromedriver` and add it in a folder accessible by the PATH (Example: your python directory. Mine is at `/Users/.../anaconda/bin/`)


### LICENSE
- MIT

### Misc
If this project was helpful to you in any way, feel free to buy me a cup of coffee :)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=QAQ4YJFQVXLMA&source=url)

For a feedback, send me an email: fernando [dot] wittmann [at] gmail [dot] com

