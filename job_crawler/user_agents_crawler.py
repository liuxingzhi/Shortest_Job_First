import requests
from lxml.html import fromstring
from job_crawler.MySQLWrapper import MySQLWrapper
import os
import time
import logging
from random import randint

logging.basicConfig(level=logging.INFO)
code = None
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0 Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'}


def get_user_agents():
    with MySQLWrapper() as db:
        url = 'https://developers.whatismybrowser.com/useragents/explore/software_name/chrome/?order_by=-times_seen'
        response = requests.get(url)
        parser = fromstring(response.text)
        query1 = "DELETE FROM user_agents"
        db.execute(query1)
        db.commit()
        for i in parser.xpath('//tbody/tr')[:200]:
            agent = i.xpath('.//td[1]/a[1]/text()')[0]
            os = i.xpath('.//td[3]/text()')[0]
            query2 = f"""insert into user_agents values('{agent}', '{os}') """
            db.execute(query2)
            db.commit()


def get_a_useragent():
    with MySQLWrapper() as db:
        query0 = "SELECT count(*) FROM user_agents"
        raw0 = db.query_one(query0)
        str0 = "{0}".format(raw0)
        result0 = str0[1:str0.__len__() - 2]
        random_line = randint(0, int(result0) - 1)
        query1 = f"""SELECT agent FROM user_agents LIMIT {random_line}, 1;"""
        raw1 = db.query_one(query1)
        str1 = "{0}".format(raw1)
        result1 = str1[2:str1.__len__() - 3]
        return result1


def main():
    get_user_agents()
    print(get_a_useragent())
main()
