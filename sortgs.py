#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
This code creates a database with a list of publications data from Google 
Scholar.
The data acquired from GS is Title, Citations, Links and Rank.
It is useful for finding relevant papers by sorting by the number of citations
This example will look for the top 100 papers related to the keyword, 
so that you can rank them by the number of citations

As output this program will plot the number of citations in the Y axis and the 
rank of the result in the X axis. It also, optionally, export the database to
a .csv file.


"""

import requests, os, datetime, argparse
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd
from time import sleep
import warnings

# Solve conflict between raw_input and input on Python 2 and Python 3
import sys
if sys.version[0]=="3": raw_input=input

# Default Parameters
KEYWORD = 'machine learning' # Default argument if command line is empty
NRESULTS = 100 # Fetch 100 articles
CSVPATH = '.' # Current folder
SAVECSV = True
SORTBY = 'Citations'
PLOT_RESULTS = False
STARTYEAR = None
now = datetime.datetime.now()
ENDYEAR = now.year # Current year
DEBUG=False # debug mode
MAX_CSV_FNAME = 255



# Websession Parameters
GSCHOLAR_URL = 'https://scholar.google.com/scholar?start={}&q={}&hl=en&as_sdt=0,5'
YEAR_RANGE = '' #&as_ylo={start_year}&as_yhi={end_year}'
#GSCHOLAR_URL_YEAR = GSCHOLAR_URL+YEAR_RANGE
STARTYEAR_URL = '&as_ylo={}'
ENDYEAR_URL = '&as_yhi={}'
ROBOT_KW=['unusual traffic from your computer network', 'not a robot']

def get_command_line_args():
    # Command line arguments
    parser = argparse.ArgumentParser(description='Arguments')
    parser.add_argument('--kw', type=str, help="""Keyword to be searched. Use double quote followed by simple quote to search for an exact keyword. Example: "'exact keyword'" """)
    parser.add_argument('--sortby', type=str, help='Column to be sorted by. Default is by the columns "Citations", i.e., it will be sorted by the number of citations. If you want to sort by citations per year, use --sortby "cit/year"')
    parser.add_argument('--nresults', type=int, help='Number of articles to search on Google Scholar. Default is 100. (carefull with robot checking if value is too high)')
    parser.add_argument('--csvpath', type=str, help='Path to save the exported csv file. By default it is the current folder')
    parser.add_argument('--notsavecsv', action='store_true', help='By default results are going to be exported to a csv file. Select this option to just print results but not store them')
    parser.add_argument('--plotresults', action='store_true', help='Use this flag in order to plot the results with the original rank in the x-axis and the number of citaions in the y-axis. Default is False')
    parser.add_argument('--startyear', type=int, help='Start year when searching. Default is None')
    parser.add_argument('--endyear', type=int, help='End year when searching. Default is current year')
    parser.add_argument('--debug', action='store_true', help='Debug mode. Used for unit testing. It will get pages stored on web archive')

    # Parse and read arguments and assign them to variables if exists
    args, _ = parser.parse_known_args()

    keyword = KEYWORD
    if args.kw:
        keyword = args.kw

    nresults = NRESULTS
    if args.nresults:
        nresults = args.nresults

    csvpath = CSVPATH
    if args.csvpath:
        csvpath = args.csvpath

    save_csv = SAVECSV
    if args.notsavecsv:
        save_csv = False

    sortby = SORTBY
    if args.sortby:
        sortby=args.sortby

    plot_results = False
    if args.plotresults:
        plot_results = True

    start_year = STARTYEAR
    if args.startyear:
        start_year=args.startyear

    end_year = ENDYEAR
    if args.endyear:
        end_year=args.endyear
    
    debug = DEBUG
    if args.debug:
        debug = True

    return keyword, nresults, save_csv, csvpath, sortby, plot_results, start_year, end_year, debug

def get_citations(content):
    out = 0
    for char in range(0,len(content)):
        if content[char:char+9] == 'Cited by ':
            init = char+9
            for end in range(init+1,init+6):
                if content[end] == '<':
                    break
            out = content[init:end]
    return int(out)

def get_year(content):
    for char in range(0,len(content)):
        if content[char] == '-':
            out = content[char-5:char-1]
    if not out.isdigit():
        out = 0
    return int(out)

def setup_driver():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.common.exceptions import StaleElementReferenceException
    except Exception as e:
        print(e)
        print("Please install Selenium and chrome webdriver for manual checking of captchas")

    print('Loading...')
    chrome_options = Options()
    chrome_options.add_argument("disable-infobars")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver

def get_author(content):
    for char in range(0,len(content)):
        if content[char] == '-':
            out = content[2:char-1]
            break
    return out

def get_element(driver, xpath, attempts=5, _count=0):
    '''Safe get_element method with multiple attempts'''
    try:
        element = driver.find_element_by_xpath(xpath)
        return element
    except Exception as e:
        if _count<attempts:
            sleep(1)
            get_element(driver, xpath, attempts=attempts, _count=_count+1)
        else:
            print("Element not found")

def get_content_with_selenium(url):
    if 'driver' not in globals():
        global driver
        driver = setup_driver()
    driver.get(url)

    # Get element from page
    el = get_element(driver, "/html/body")
    c = el.get_attribute('innerHTML')

    if any(kw in el.text for kw in ROBOT_KW):
        raw_input("Solve captcha manually and press enter here to continue...")
        el = get_element(driver, "/html/body")
        c = el.get_attribute('innerHTML')


    return c.encode('utf-8')


def main():
    # Get command line arguments
    keyword, number_of_results, save_database, path, sortby_column, plot_results, start_year, end_year, debug = get_command_line_args()

    # Create main URL based on command line arguments
    if start_year:
        GSCHOLAR_MAIN_URL = GSCHOLAR_URL + STARTYEAR_URL.format(start_year)
    else:
        GSCHOLAR_MAIN_URL = GSCHOLAR_URL

    if end_year != now.year:
        GSCHOLAR_MAIN_URL = GSCHOLAR_MAIN_URL + ENDYEAR_URL.format(end_year)

    if debug:
        GSCHOLAR_MAIN_URL='https://web.archive.org/web/20210314203256/'+GSCHOLAR_URL

    # Start new session
    session = requests.Session()
    #headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    # Variables
    links = []
    title = []
    citations = []
    year = []
    author = []
    rank = [0]

    # Get content from number_of_results URLs
    for n in range(0, number_of_results, 10):
        #if start_year is None:
        url = GSCHOLAR_MAIN_URL.format(str(n), keyword.replace(' ','+'))
        if debug:
            print("Opening URL:", url)
        #else:
        #    url=GSCHOLAR_URL_YEAR.format(str(n), keyword.replace(' ','+'), start_year=start_year, end_year=end_year)

        print("Loading next {} results".format(n+10))
        page = session.get(url)#, headers=headers)
        c = page.content
        if any(kw in c.decode('ISO-8859-1') for kw in ROBOT_KW):
            print("Robot checking detected, handling with selenium (if installed)")
            try:
                c = get_content_with_selenium(url)
            except Exception as e:
                print("No success. The following error was raised:")
                print(e)

        # Create parser
        soup = BeautifulSoup(c, 'html.parser')

        # Get stuff
        mydivs = soup.findAll("div", { "class" : "gs_r" })

        for div in mydivs:
            try:
                links.append(div.find('h3').find('a').get('href'))
            except: # catch *all* exceptions
                links.append('Look manually at: '+url)

            try:
                title.append(div.find('h3').find('a').text)
            except:
                title.append('Could not catch title')

            try:
                citations.append(get_citations(str(div.format_string)))
            except:
                warnings.warn("Number of citations not found for {}. Appending 0".format(title[-1]))
                citations.append(0)

            try:
                year.append(get_year(div.find('div',{'class' : 'gs_a'}).text))
            except:
                warnings.warn("Year not found for {}, appending 0".format(title[-1]))
                year.append(0)

            try:
                author.append(get_author(div.find('div',{'class' : 'gs_a'}).text))
            except:
                author.append("Author not found")

            rank.append(rank[-1]+1)

        # Delay 
        sleep(0.5)

    # Create a dataset and sort by the number of citations
    data = pd.DataFrame(list(zip(author, title, citations, year, links)), index = rank[1:],
                        columns=['Author', 'Title', 'Citations', 'Year', 'Source'])
    data.index.name = 'Rank'

    # Add columns with number of citations per year
    data['cit/year']=data['Citations']/(end_year + 1 - data['Year'])
    data['cit/year']=data['cit/year'].round(0).astype(int)

    # Sort by the selected columns, if exists
    try:
        data_ranked = data.sort_values(by=sortby_column, ascending=False)
    except Exception as e:
        print('Column name to be sorted not found. Sorting by the number of citations...')
        data_ranked = data.sort_values(by='Citations', ascending=False)
        print(e)

    # Print data
    print(data_ranked)

    # Plot by citation number
    if plot_results:
        plt.plot(rank[1:],citations,'*')
        plt.ylabel('Number of Citations')
        plt.xlabel('Rank of the keyword on Google Scholar')
        plt.title('Keyword: '+keyword)
        plt.show()

    # Save results
    if save_database:
        fpath_csv = os.path.join(path,keyword.replace(' ','_')+'.csv')
        fpath_csv = fpath_csv[:MAX_CSV_FNAME]
        data_ranked.to_csv(fpath_csv, encoding='utf-8')

if __name__ == '__main__':
        main()
