import requests
import os
import sys
import string
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as bs
from job_crawler.MySQLWrapper import MySQLWrapper
from typing import Optional, List, Sequence, Deque, Dict, Tuple, Union
from MySQLdb import IntegrityError

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'

job_list_file = "job_list.txt"


def init_soup(url: str) -> Optional[BeautifulSoup]:
    kv = {'user-agent': user_agent}
    try:
        r = requests.get(url, headers=kv)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        html = r.text
        soup = bs(html, 'html.parser')
        # print(soup.prettify())
    except Exception as e:
        print(e, file=sys.stderr)
        print('failed to crawl:' + str(r.status_code))
        return None
    return soup


def init_table(category_list: List[str]) -> None:
    with MySQLWrapper() as db:
        sql = """CREATE TABLE IF NOT EXISTS job_categories
            (
              category VARCHAR(100) NOT NULL,
              crawled  BOOL DEFAULT FALSE,
              PRIMARY KEY (category)
            )"""
        db.execute(sql)

        for category in category_list:
            sql = f"""insert into job_categories(category) values('{category}') """
            try:
                db.execute(sql)
            except IntegrityError as e:
                continue
        db.commit()


def get_job_category_list() -> List[str]:
    alphas = string.ascii_uppercase[:27]
    url = 'https://www.indeed.com/find-jobs.jsp?title='
    # print(alphas)
    # i = 0
    job_list = []
    for a in alphas:
        soup = init_soup(url + a)
        tags = soup.findAll("a", {"class": "jobTitle"})
        for tag in tags:
            job_list.append(tag.text)
    print(job_list, len(job_list))
    return job_list


def write_to_file(file_path: str, category_list: List[str]) -> None:
    with open(file_path, "w+") as f:
        for job in category_list:
            f.write(job.lower() + "\n")


if __name__ == '__main__':
    job_list = get_job_category_list()
    init_table(job_list)
    write_to_file("job_list.txt", job_list)
