This Python code ranks publications data from Google Scholar by the number
of citations.
It is useful for finding relevant papers in a specific field.

The data acquired from Google Scholar is Title, Citations, Links and Rank.
The example of the code will look for the top 100 papers related to the keyword
'non intrusive load monitoring', and rank them by the number of citations
As output this program will plot the number of citations in the Y axis and the
rank of the result in the X axis. It also, optionally, export the database to
a .csv file.

## Update: Command-Line Interface
The python code is now available via command-line interface for easier usage and control.

**To get started you can view the full help guide using the following command
```
~ python google_scholar_sort.py --help
```

**Sample output
```

Sorting Google Scholar

Usage:
    google_scholar_sort.py <keywords>
    google_scholar_sort.py <keywords> [--results=<numberOfResults>] [--output=<path>]
    google_scholar_sort.py <keywords> [--results=<numberOfResults>]
    google_scholar_sort.py <keywords> [--output=<path>]
    google_scholar_sort.py <keywords> [--output=<path>] [--results=<numberOfResults>]

Options:
    <keywords>                   This is the search term that will be used as a keyword for search
                                 Ex... "Machine Learning In Financial Engineer"
    --results=<numberOfResults>  Specify number of results to look for on Google Scholar [default: 100]
    --output=<path>              Output file path (default: same directory of the .py file)
                                 NOTE: don't include path between quotes
```

####Example

**Retrieving the best 200 results about _"Bioinformatics"_ and saving the output inside _"results"_ file on the desktop

```
~ python google_scholar_sort.py "Bioinformatics" --results=200 --output=C:/Users/Mahmoud/Desktop/Results
```

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
