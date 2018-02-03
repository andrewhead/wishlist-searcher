"""
Fetch records for a certain type of search on Craigslist.
"""
from __future__ import unicode_literals, print_function
import logging

from datetime import datetime
import time
from time import strptime, mktime
import re
import urllib
import os.path

import schedule
from bs4 import BeautifulSoup as Soup
from tabulate import tabulate
from mailer import Mailer, Message
import cache


logging.basicConfig(level=logging.INFO, format="%(message)s")
SMTP_CONFIG = 'smtp.conf'
QUERY_FILE = os.path.expanduser(os.path.join("~", "wishlist_queries.txt"))
ADDRESSES = [
    # 'head.andrewm@gmail.com',
    'ac.mullin@gmail.com',
]


def get_records(query):
    """
    Fetch records for a Craigslist search for a query
    """
    # Get the latest page in our neighborhood
    resp = cache.get_session().get("http://sfbay.craigslist.org/search/eby/sss", params={
        'query': urllib.quote_plus(query),
    })
    soup = Soup(resp.text, "html.parser")

    # Go through each of the search results
    records = []
    for row in soup.select('li.result-row'):

        # Get the date of the post
        timestamp = row.find('time')['datetime']
        date_time = datetime.fromtimestamp(mktime(
            strptime(timestamp, "%Y-%m-%d %H:%M")
        ))

        # ... link ....
        link = row.find('a', attrs={'class': 'hdrlnk'})
        href = link['href']
        desc = link.text

        # ... item price ...
        prices = row.select('.result-price')
        price = "?"
        if prices:
            price = prices[0].text.replace('$', '')

        # ... where the item's at ...
        neighborhoods = row.select('.result-hood')
        neighborhood = "?"
        if neighborhoods:
            neighborhood = re.search(r'\((.*)\)', neighborhoods[0].text).group(1)

        # Only save the record if it's from the last N days
        if abs((date_time - datetime.now()).days) <= 2:
            records.append([
                '%d/%d' % (date_time.month, date_time.day), desc[:50] + "...",
                price, neighborhood, href,
            ])

    return records


def send_mail(query_records, addrs=None):
    """
    Send an email for a set of records to a list of email addresses.
    """
    addresses = addrs
    if addrs is None:
        addresses = ADDRESSES

    with open(SMTP_CONFIG) as conf:
        lines = conf.readlines()
        user = lines[0].strip()
        password = lines[1].strip()

    # Pretty-print the results!
    message_html = ""
    for (query, records) in query_records.items():
        message_html += "<p>Items listed for \"" + query + "\"</p></br/>"
        table = tabulate(
            records,
            headers=['Date', 'What', 'Price', 'Where', 'Link'])
        message_html += "<pre>" + table + "</pre><br/><br/>"

    sender = 'openairandrew@gmail.com'
    message = Message(From=sender, To=addresses, charset='utf-8')
    message.Subject = "Updates for East Bay Craigslist: \"" + "\", \"".join(query_records) + "\""
    message.Html = message_html
    sender = Mailer('smtp.gmail.com:587', use_tls=True, usr=user, pwd=password)
    sender.send(message)


def job():
    """
    The main program.
    """
    print("Running job")
    try:

        queries = []
        with open(QUERY_FILE) as query_file:
            queries = [q.strip() for q in query_file.readlines()]

        query_records = {}
        for query_entry in queries:
            query_records[query_entry] = get_records(query_entry)

        send_mail(query_records)

    # There may be some exception in execution: connection (if the
    # computer has been closed and is re-opening), file-not-found
    # if someone has deleted the configuration file, or something
    # else.  Just catch them all and make sure the program doesn't
    # cancel the other scheduled jobs.
    except Exception as exception:
        print(exception)
        return


if __name__ == '__main__':

    # Run this every (hour / day / whatever)
    schedule.every(1).minute.do(job)

    # Just something to keep the program alive
    while True:
        schedule.run_pending()
        time.sleep(1)
