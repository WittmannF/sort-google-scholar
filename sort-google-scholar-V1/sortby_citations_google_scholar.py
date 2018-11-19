# -*- coding: utf-8 -*-
"""
This code creates a database with a list of publications data from Google 
Scholar.
The data acquired from GS is Title, Citations, Links and Rank.
It is useful for finding relevant papers by sorting by the number of citations
This example will look for the top 100 papers related to the keyword 
'non intrusive load monitoring', so that you can rank them by the number of citations

As output this program will plot the number of citations in the Y axis and the 
rank of the result in the X axis. It also, optionally, export the database to
a .csv file.

Before using it, please update the initial variables

"""

import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd


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

def get_author(content):
    for char in range(0,len(content)):
        if content[char] == '-':
            out = content[2:char-1]
            break
    return out

# Update these variables according to your requirement
keyword = "'non intrusive load monitoring'" # the double quote will look for the exact keyword,
                                            # the simple quote will also look for similar keywords
number_of_results = 100 # number of results to look for on Google Scholar
save_database = False # choose if you would like to save the database to .csv
path = 'C:/_wittmann/nilm_100_exact_author.csv' # path to save the data

# Start new session
session = requests.Session()

# Variables
links = list()
title = list()
citations = list()
year = list()
rank = list()
author = list()
rank.append(0) # initialization necessary for incremental purposes

# Get content from 1000 URLs
for n in range(0, number_of_results, 10):    
    url = 'https://scholar.google.com/scholar?start='+str(n)+'&q='+keyword.replace(' ','+')
    page = session.get(url)
    c = page.content
    
    # Create parser
    soup = BeautifulSoup(c, 'html.parser')
    
    # Get stuff
    mydivs = soup.findAll("div", { "class" : "gs_r" })
    
    for div in mydivs:
        try:
            links.append(div.find('h3').find('a').get('href'))
        except: # catch *all* exceptions
            links.append('Look manually at: https://scholar.google.com/scholar?start='+str(n)+'&q=non+intrusive+load+monitoring')
        
        try:
            title.append(div.find('h3').find('a').text)
        except: 
            title.append('Could not catch title')
            
        citations.append(get_citations(str(div.format_string)))
        year.append(get_year(div.find('div',{'class' : 'gs_a'}).text))
        author.append(get_author(div.find('div',{'class' : 'gs_a'}).text))
        rank.append(rank[-1]+1)

# Create a dataset and sort by the number of citations
data = pd.DataFrame(zip(author, title, citations, year, links), index = rank[1:], 
                    columns=['Author', 'Title', 'Citations', 'Year', 'Source'])
data.index.name = 'Rank'

data_ranked = data.sort_values(by='Citations', ascending=False)
print data_ranked

# Plot by citation number
plt.plot(rank[1:],citations,'*')
plt.ylabel('Number of Citations')
plt.xlabel('Rank of the keyword on Google Scholar')
plt.title('Keyword: '+keyword)

# Save results
if save_database:
    data_ranked.to_csv(path, encoding='utf-8') # Change the path
        
