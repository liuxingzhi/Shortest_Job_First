from job_crawler.clean_data import clean_data
from job_crawler.crawl_job_titles import get_job_category_list, run_job_title_crawler, init_table, \
    reset_job_category_table
from job_crawler.ip_address_crawler import get_potential_proxies_list, get_a_proxy, run_proxy_crawler
from job_crawler.glassdoor_crawler import dispatch_job_categories
from job_crawler.user_agents_crawler import get_a_useragent, get_user_agents, run_user_agent_crawler
from job_crawler.MySQLWrapper import MySQLWrapper
from job_crawler.logo_crawler import logo_crawler_job_dispatcher
import os
import logging
import datetime
from multiprocessing import Manager, Process

logging_file_dir = "loggings"
if not os.path.exists(logging_file_dir):
    os.makedirs(logging_file_dir)

def init_logging_database():
    with MySQLWrapper() as db:
        sql = """CREATE TABLE IF NOT EXISTS crawler_system_logging_table
                (
                    crawl_id          int NOT NULL,
                    start_time        datetime,
                    end_time          datetime,
                    in_progress         bool,
                    succeeded         bool,
                    logging_file_path text
                );"""
        db.execute(sql)
        db.commit()


def run_system():
    init_logging_database()
    # select largest crawl_id and we increase by one
    run_id = current_run_id()
    cur_log_file_path = os.path.join(logging_file_dir, f"{str(run_id)}_record.log")
    print(cur_log_file_path)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=logging.DEBUG, filename=cur_log_file_path, filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
    record_start_status(run_id, cur_log_file_path)

    pro1 = Process(target=run_user_agent_crawler, daemon=False)
    pro2 = Process(target=run_proxy_crawler, daemon=False)
    pro3 = Process(target=run_job_title_crawler, daemon=False)
    pro1.start()
    pro2.start()
    pro3.start()
    pro1.join()
    pro2.join()
    pro3.join()

    pro4 = Process(target=dispatch_job_categories, args=(2,), daemon=False)
    pro4.start()
    pro4.join()

    print("should not come here")
    logo_crawler_job_dispatcher(20)
    clean_data()
    record_end_status(run_id)


def current_run_id() -> int:
    with MySQLWrapper() as db:
        sql = """ select max(crawl_id) from crawler_system_logging_table"""
        result = db.query_all(sql)
    if result[0][0] is None:
        return 1
    else:
        return result[0][0] + 1


def record_start_status(crawl_id: int, cur_log_file_path: str):
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with MySQLWrapper() as db:
        sql = f"""insert into crawler_system_logging_table
                (crawl_id, start_time, in_progress, logging_file_path,succeeded) 
                values ({crawl_id},'{start_time}',TRUE,'{cur_log_file_path}',FALSE)"""
        db.insert_one(sql)


def record_end_status(crawl_id: int):
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with MySQLWrapper() as db:
        sql = f"""update crawler_system_logging_table c1
                    set c1.end_time = '{end_time}', c1.succeeded = TRUE, c1.in_progress = FALSE
                    where c1.crawl_id = {crawl_id}"""
        db.execute(sql)
        db.commit()


if __name__ == '__main__':
    run_system()
