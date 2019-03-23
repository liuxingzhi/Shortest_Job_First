import requests
from bs4 import BeautifulSoup
from queue import Queue
import threading
import re
import os
import time
import logging
from job_crawler.MySQLWrapper import MySQLWrapper
import MySQLdb
from MySQLdb import OperationalError, IntegrityError

logging.basicConfig(level=logging.INFO)
code = None
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0 Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'}


def getHTMLText(url, encode=None):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        # print(r.status_code)
        r.raise_for_status()
        if encode is None:
            r.encoding = r.apparent_encoding
            global code
            code = r.encoding
        else:
            r.encoding = encode
        # print(r.encoding)
        return r.text
    except Exception as e:
        logging.log(logging.INFO, str(e))
        return ""


def get_picture_content(url):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        # print(r.status_code)
        r.raise_for_status()
        return r.content
    except Exception as e:
        logging.log(logging.INFO, str(e))
        return ""


def main():
    pass


if __name__ == '__main__':
    main()
