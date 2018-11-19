This Python code ranks publications data from Google Scholar by the number 
of citations.
It is useful for finding relevant papers in a specific field. 

The data acquired from Google Scholar is Title, Citations, Links and Rank.
The example of the code will look for the top 100 papers related to the keyword 
'non intrusive load monitoring', and rank them by the number of citations
As output this program will plot the number of citations in the Y axis and the 
rank of the result in the X axis. It also, optionally, export the database to
a .csv file.
Please update the keyword and other initialization variables

### Usage
```
usage: google_scholar_sort.py [-h] [--sortby SORTBY] [--nresults NRESULTS]
                              [--csvpath CSVPATH] [--notsavecsv]
                              [--plotresults] [--startyear STARTYEAR]
                              [--endyear ENDYEAR]
                              keyword

Arguments

positional arguments:
  keyword               Keyword to be searched. Use double quote followed by
                        simple quote to search for an exact keyword. Example:
                        "'exact keyword'"

optional arguments:
  -h, --help            show this help message and exit
  --sortby SORTBY       Column to be sorted by. Default is by the number of
                        citations. If you want to sort by the number of
                        citations per year, use --sortby "cit/year"
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

### Examples

### Requirements
If you install anaconda, all of those requirements will be met:
- Python 2.7 or Python 3
- Requests: `pip install requests`
- Beautiful Soup: `pip install beautifulsoup4`
- Pandas: `pip install pandas`
- Matplotlib: `pip install matplotlib`

### Update: Google Robot Checking
If you are having problems with Google robot checking, as a suggestion, you can try using a proxy. Follow those steps:

1. Go to the website https://free-proxy-list.net/ and pick one proxy (example: 200.162.142.178). 

2. Add a new line with the chosen proxy, for example: 
```
proxies = {
  'http': 'http://200.162.142.178:3128',
  'https': 'http://200.162.142.178:3128',
}
```

3. Add `proxies` as an attribute in `session.get`. In other words, change the line with `page = session.get(url)` to `page = session.get(url, proxies=proxies)`.

4. I hope that works! For a feedback, send me an email: fernando [dot] wittmann [at] gmail [dot] com

If this project was helpful to you in any way, feel free to buy me a cup of coffee :)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=QAQ4YJFQVXLMA&source=url)
