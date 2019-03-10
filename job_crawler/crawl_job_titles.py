import requests
import os
import sys
import string
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as bs

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'

job_list_file = "job_list.txt"


def init_soup(url: str) -> BeautifulSoup:
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
    return soup


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

with open(job_list_file, "w") as f:
    for job in job_list:
        f.write(job.lower() + "\n")
