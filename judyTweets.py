#! python3
# judyTweets.py - scrapes judge judy quotes from IMDB and saves them as shelf file
    # tweets one quote daily at 9am to your twitter account

import os, bs4, requests, shelve, datetime, time, math
from twitter import *

ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET =''

# FUNCTIONS
#----------------------------------------------------------------------------------------
# scrapes Judge Judy Quotes from IMDB
def scrapeQuotes():
    quotesList= []
    website = 'http://www.imdb.com/title/tt0115227/quotes'
    res = requests.get(website)
    soup = bs4.BeautifulSoup(res.text)
    quotes = soup.select('div[class="sodatext"]')
    for i in quotes:
        quotesList.append(i.get_text()[2:])
    return quotesList

# save quotes as shelve file
def saveQuotes(list):
    quoteFile = shelve.open('judyQuotesList')
    quotes = []
    for i in list:
        quotes.append(i)
    quoteFile['quotes']= quotes

# keeps track of which quote is next
def quoteCounter():
    numberFile = shelve.open("currentQuote")
    currentNumber = numberFile['current_quote']
    quoteFile = shelve.open('judyQuotesList')
    numberOfQuotes = quoteFile['quotes']
    if currentNumber >= len(numberOfQuotes)-1:
        numberFile['current_quote'] = 0
        numberFile.close()
        quoteFile.close()
        return 0
    else:
        numberFile['current_quote'] += 1
        numberFile.close()
        quoteFile.close()
        return currentNumber


# returns current quote number
def currentQuote():
    numberFile = shelve.open('currentQuote')
    number = numberFile['current_quote']
    numberFile.close()
    return number

# determines if it is time to post a new tweet
def time_to_post():
    now = datetime.datetime.now()
    if now.hour == 9:
        return True
    else:
        return False

# posts string to twitter
def tweet(string):
    if not string.isspace() and string.strip():
        t = Twitter(auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
        t.statuses.update(status=string)
    else:
        pass

# posts current JJ quote to twitter account
def post_it():
    if time_to_post():
        quoteCounter()      # updates quote count
        shelfFile = shelve.open('judyQuotesList')
        quote = shelfFile['quotes'][currentQuote()]
        if len(quote) > 140:
            numtwts = round((len(quote)/140) + 0.5)     # determines the number of tweets needed to post whole quote. adding 0.5 to len(quote)/140 rounds up to nearest whole number
            for i in range(0, numtwts+1):
                snip = quote[((i-1)*140):min(len(quote)+1, i*140)]
                tweet(snip)
        else:
            tweet(quote)
        shelfFile.close()
        time.sleep(1)
        post_it()
    else:
        time.sleep(1)
        post_it()


# RUNS PROGRAM
#------------------------------------------------------------------------------------

# creates quote shelf file if doesn't already exist
if os.path.exists("./currentQuote.db"):
    pass
else:
    shelfFile = shelve.open("currentQuote")
    current_quote = 0
    shelfFile['current_quote'] = current_quote
    shelfFile.close()

# creates shelf with JJ quotes if doesn't already exist
if os.path.exists("./judyQuotesList.db"):
    pass
else:
    saveQuotes(scrapeQuotes())

# runs program
post_it()



