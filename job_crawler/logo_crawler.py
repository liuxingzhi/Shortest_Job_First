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

logging.basicConfig(level=logging.INFO)
code = None
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0 Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'}

imgs_task_queue = Queue()
saved_dir = os.path.join("..", "media", "company_logos")


def getHTMLText(url: str, encode=None) -> str:
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
        return r.text
    except Exception as e:
        logging.log(logging.INFO, str(e))
        return ""


def get_picture_content(url: str) -> Optional[bytes]:
    try:
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
            stored_path = os.path.join(saved_dir, company_id + ".png")
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
                    logo_path = os.path.join("company", company_id + ".png")
                    sql = f"""update company_data_unclean as c
                            set c.logo_path = '{logo_path}'
                            where c.company_id = {company_id}
                            """
                    db.execute(sql)
                    db.commit()
                    print(f"downloaded {company_id} logo")


def job_dispatcher(thread_num: int) -> None:
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
    job_dispatcher(4)
