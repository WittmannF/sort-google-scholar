### Sort Google Scholar by the Number of Citations
This Python code ranks publications data from Google Scholar by the number 
of citations.
It is useful for finding relevant papers in a specific field. 

The data acquired from Google Scholar is Title, Citations, Links and Rank.
The example of the code will look for the top 100 papers related to the keyword, 
and rank them by the number of citations
As output the file will return a .csv file ranked by the number of citations.

### Updated Code: Usage
```
usage: python sortgs.py [-h] [--sortby SORTBY] [--nresults NRESULTS]
                              [--csvpath CSVPATH] [--notsavecsv]
                              [--plotresults] [--startyear STARTYEAR]
                              [--endyear ENDYEAR]
                              keyword

Example: python sortgs.py "machine learning"

positional arguments:
  keyword               Keyword to be searched. Use double quote followed by
                        simple quote to search for an exact keyword. Example:
                        "'exact keyword'"

optional arguments:
  -h, --help            show this help message and exit
  --sortby SORTBY       String. Column to be sorted by. Default is by the number of
                        citations. If you want to sort by the number of
                        citations per year, use --sortby "cit/year"
  --nresults NRESULTS   Int. Number of articles to search on Google Scholar.
                        Default is 100. (carefull with robot checking if value
                        is too high)
  --csvpath CSVPATH     String. Path to save the exported csv file. By default it is
                        the current folder
  --notsavecsv          Flag. By default results are going to be exported to a csv
                        file. Select this option to just print results but not
                        store them
  --plotresults         Flag. Use this flag in order to plot the results with the
                        original rank in the x-axis and the number of citaions
                        in the y-axis. Default is False
  --startyear STARTYEAR Int. Start year when searching. Default is None
  --endyear ENDYEAR     Int. End year when searching. Default is current year
```

### Example
The following code will search for the top 100 results, rank by number of citations and save as a .csv file (same name of the keyword):
```
$python sortgs.py "machine learning"
```

Sorted by number of citations per year:
```
$python sortgs.py "machine learning" --sortby "cit/year"
```

From 2005 to 2015:
```
$python sortgs.py "machine learning" --startyear 2005 --endyear 2015
```


### Requirements
If you install anaconda, all of those requirements (except s) are going to be met:
- Python 2.7 or Python 3
- Requests: `pip install requests`
- Beautiful Soup: `pip install beautifulsoup4`
- Pandas: `pip install pandas`
- Matplotlib: `pip install matplotlib`

The following instalations are optional, if having problems with robot checking:
- Selenium: `pip install selenium`
- ChromeDriver: http://chromedriver.chromium.org/
    - After downloading chromedriver, make sure to add it in a folder accessible from the PATH


### LICENSE
- MIT

### Misc
If this project was helpful to you in any way, feel free to buy me a cup of coffee :)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=QAQ4YJFQVXLMA&source=url)

For a feedback, send me an email: fernando [dot] wittmann [at] gmail [dot] com

