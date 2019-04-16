import requests
from typing import List, Dict, Deque, Sequence, Optional, Tuple
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
from job_crawler.ip_address_crawler import get_a_proxy
from job_crawler.user_agents_crawler import get_a_useragent

logging.basicConfig(level=logging.INFO)
code = None
imgs_task_queue = Queue()
saved_dir = os.path.join("..", "media", "company_logos")
if not os.path.exists(saved_dir):
    os.makedirs(saved_dir)


def timeit(func):
    """一个计时器"""

    def wrapper(*args, **kwargs):
        start = time.clock()
        response = func(*args, **kwargs)
        end = time.clock()
        print('time spend:', end - start)
        return response

    return wrapper


def getHTMLText(url: str, encode: str = None, proxy_dict: Dict[str, str] = None) -> str:
    try:
        user_agent = get_a_useragent()
        headers = {'User-Agent': user_agent}
        r = requests.get(url, headers=headers, timeout=10, proxies=proxy_dict)
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


def get_picture_content(url: str, anonymous=False) -> Optional[bytes]:
    try:
        user_agent = get_a_useragent()
        headers = {'User-Agent': user_agent}
        proxy = get_a_proxy()
        if anonymous:
            r = requests.get(url, headers=headers, timeout=10, proxies=proxy)
        else:
            r = requests.get(url, headers=headers, timeout=10)
        # print(r.status_code)
        r.raise_for_status()
        return r.content
    except Exception as e:
        logging.log(logging.INFO, str(e))
        return None


def save_imgs_task() -> None:
    with MySQLWrapper() as db:
        while True:
            url_task: Optional[Tuple[str, str]] = imgs_task_queue.get()
            if url_task is None:
                break
            company_id, url = url_task
            stored_path = os.path.join(saved_dir, str(company_id) + ".png")
            # print("saving image")
            # get_picture_content(url)
            with open(stored_path, 'wb') as f:
                try:
                    f.write(get_picture_content(url))
                except Exception as e:
                    logging.log(logging.INFO, f"failed at:{company_id}, {str(e)}")
                else:
                    sql = f"""update company_logo_downloaded as c
                                set c.downloaded = true
                                where c.company_id = {company_id}
                            """

                    db.execute(sql)
                    logo_path = os.path.join("company", str(company_id) + ".png")
                    sql = f"""update company_data_unclean as c
                            set c.logo_path = '{logo_path}'
                            where c.company_id = {company_id}
                            """
                    db.execute(sql)
                    db.commit()
                    print(f"downloaded {company_id} logo")


def logo_crawler_job_dispatcher(thread_num: int) -> None:
    with MySQLWrapper() as db:
        sql = """select c.company_id, c.logo_url
                    from company_data_unclean as c
                    inner join company_logo_downloaded as c2
                    on c.company_id = c2.company_id
                    where c2.downloaded = false
                    order by c.company_id
                    limit 12
                """
        result = db.query_all(sql)
        for r in result:
            imgs_task_queue.put(r)

    downloading_threads: List[threading.Thread] = []
    for i in range(thread_num):
        thread = threading.Thread(target=save_imgs_task)
        thread.setDaemon(False)
        downloading_threads.append(thread)

    for i in range(thread_num):
        downloading_threads[i].start()

    for i in range(thread_num):
        imgs_task_queue.put(None)

    for thread in downloading_threads:
        thread.join()


def init():
    with MySQLWrapper() as db:
        sql1 = """CREATE TABLE IF NOT EXISTS company_logo_downloaded
                    (
                      company_id VARCHAR(100) NOT NULL,
                      downloaded  BOOL DEFAULT FALSE,
                      PRIMARY KEY (company_id)
                    )       
                """

        sql2 = """
                insert into company_logo_downloaded(company_id)
                select company_id
                from company_data_unclean;
                """

        db.execute(sql1)
        try:
            db.execute(sql2)
            db.commit()
        except IntegrityError as e:
            pass

    if not os.path.exists(saved_dir):
        os.makedirs(saved_dir)


if __name__ == '__main__':
    init()
    logo_crawler_job_dispatcher(4)
