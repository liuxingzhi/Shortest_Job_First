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
glassdoor_main_url = "https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=software&sc.keyword=software&locT=&locId=&jobType="


def getHTMLText(url: str, encode=None, proxy=None) -> str:
    try:
        r = requests.get(url, headers=headers, timeout=10, proxies=proxy)
        # print(r.status_code)
        r.raise_for_status()
        if encode is None:
            r.encoding = r.apparent_encoding
            global code
            code = r.encoding
        else:
            r.encoding = encode
        return r.text
    except Exception as e:
        logging.log(logging.INFO, str(e))
        return ""


def get_proxies():
    with MySQLWrapper() as db:
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        query1 = "DELETE FROM proxies"
        db.execute(query1)
        db.commit()
        for i in parser.xpath('//tbody/tr')[:5000]:
            # i.xpath('.//td[3][contains(text(),"US")]') &
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                ip = i.xpath('.//td[1]/text()')[0]
                port = i.xpath('.//td[2]/text()')[0]
                location = i.xpath('.//td[3]/text()')[0]
                last_checked = i.xpath('.//td[8]/text()')[0]
                proxy = ":".join([ip, port])
                print(proxy)
                text1 = getHTMLText(glassdoor_main_url, proxy)
                if text1 == "":
                    print("failed")
                else:
                    query2 = f"""insert into proxies values('{ip}', '{port}', '{location}','{last_checked}') """
                    db.execute(query2)
                    db.commit()
                    print("success")


def get_a_proxy():
    with MySQLWrapper() as db:
        query0 = "SELECT count(*) FROM proxies"
        raw0 = db.query_one(query0)
        str0 = "{0}".format(raw0)
        result0 = str0[1:str0.__len__() - 2]
        random_line = randint(0, int(result0) - 1)
        query1 = f"""SELECT ip FROM proxies LIMIT {random_line}, 1;"""
        raw1 = db.query_one(query1)
        query2 = f"""SELECT port FROM proxies LIMIT {random_line}, 1;"""
        raw2 = db.query_one(query2)
        str1 = "{0}".format(raw1)
        str2 = "{0}".format(raw2)
        result1 = str1[2:str1.__len__() - 3]
        result2 = str2[2:str2.__len__() - 3]
        result = ":".join([result1, result2])
        return result


def main():
    get_proxies()
    get_a_proxy()
main()
