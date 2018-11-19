## Sort Google Scholar Results V1 
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


### Google Robot Checking (Does not seem to work)
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

