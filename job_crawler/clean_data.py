from typing import List, Dict, Deque, Sequence, Optional, Tuple
from bs4 import BeautifulSoup
from queue import Queue
import threading
import re
import os
import time
import logging
from job_crawler.MySQLWrapper import MySQLWrapper


def clean_job_and_insert():
    with MySQLWrapper() as db:
        table_name = "job"
        db.delete_from(table_name, "1=1")
        sql = """insert into job 
                select * from job_data_unclean as j2
                where j2.job_description is not null
                and j2.job_title is not null"""
        db.execute(sql)
        db.commit()


def clean_company_and_insert():
    with MySQLWrapper() as db:
        table_name = "company"
        db.delete_from(table_name, "1=1")
        sql = """insert into company
                select * from company_data_unclean as c2
                where c2.company_name is not null
                and c2.logo_url is not null"""
        db.execute(sql)
        db.commit()


def clean_data():
    clean_company_and_insert()
    clean_job_and_insert()


if __name__ == '__main__':
    clean_data()
