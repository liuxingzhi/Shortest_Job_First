import selenium
from threading import Thread, Lock, Condition, Event
from typing import List, Dict, Tuple, Sequence
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
import os
import time
from bs4 import BeautifulSoup
import pandas as pd
import signal
import sys
import platform
from time import sleep
from datetime import datetime, timedelta
from collections import namedtuple
import re
from queue import Queue
import threading
import multiprocessing
from multiprocessing import Manager, Process
from job_crawler.MySQLWrapper import MySQLWrapper
import MySQLdb
from MySQLdb import OperationalError, IntegrityError
import logging

logging.basicConfig(level=logging.INFO)

glassdoor_main_url = "https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=software&sc.keyword=software&locT=&locId=&jobType="
time_limit = 12
job_list_file = "job_list.txt"
job_list = []


# def sign_in():
#     my_email = "abelliu@gmail.com"
#     password = "cs4112019"
#     driver.get(glassdoor_main_url)
#     driver.implicitly_wait(time_limit)
#     """
#     WebDriverWait wait = new WebDriverWait(driver,30);
#     wait.until(ExpectedConditions.presenceOfElementLocated(By.xpath("//*[@id='campaignListTable']")));   /*examining the xpath for a search
#     box*/
#     driver.findElement(By.xpath("//*[@id='campaignListTable']")).sendKeys("TEXT");   /*enter text in search
#     box*/
#     """
#     sign_in_button = driver.find_element_by_xpath("""//*[@id="TopNav"]//*[contains(text(), 'Sign In')]""")
#     sign_in_button.click()
#
#     driver.implicitly_wait(time_limit)
#     username_tag = driver.find_element_by_id("userEmail")
#     username_tag.send_keys(my_email)
#     password_tag = driver.find_element_by_id("userPassword")
#     password_tag.send_keys(password)
#     driver.find_element_by_xpath("""//*[@id="LoginModal"]/div/div/div[2]/div/button//*[contains(text(), 'Sign In')]""")

def get_brower():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # 运行时关闭窗口
    # 使用同一目录下的chromedriver进行模拟
    browser_driver_address = str
    if platform.system() == "Windows":
        browser_driver_address = "chromedriver.exe"
    elif platform.system() == "Darwin":
        browser_driver_address = "chromedriver_2.45_mac"
    elif platform.system() == "Linux":
        browser_driver_address = "chromedriver_2.36_ubuntu16.04"
    else:
        browser_driver_address = "chromedriver_2.36_ubuntu16.04"

    driver_path = os.path.join(os.path.abspath("."), "browser_drivers", browser_driver_address)

    print("chrome_drive:", driver_path)
    driver = webdriver.Chrome(driver_path, chrome_options=chrome_options)
    return driver


def crawl_bunch_of_job(job_list: List[str], threadID: int):
    print(threadID)
    driver = get_brower()
    for job in job_list:
        with open("job_crawled.txt", "a+") as f:
            f.write(job + "\n")
        try:
            crawl_one_job_title(job, driver)
        except Exception as e:
            logging.log(logging.INFO, f"出错了，跳过当前job{job}:" + str(e))
    driver.quit()


def crawl_one_job_title(job: str, driver: webdriver.Chrome):
    # go to the main page of glassdoor
    driver.get(glassdoor_main_url)
    driver.implicitly_wait(time_limit)
    keyword = driver.find_element_by_id("sc.keyword")
    keyword.clear()
    keyword.send_keys(job)
    location = driver.find_element_by_id("sc.location")
    location.clear()
    driver.find_element_by_id("HeroSearchButton").click()
    with MySQLWrapper() as conn:
        pages_to_crawl = 5
        for i in range(pages_to_crawl):
            try:
                try:
                    job_ul = driver.find_element_by_xpath("""//*[@id="MainCol"]/div/ul""")
                except selenium.common.exceptions.NoSuchElementException as e:
                    # 如果没找到，那这个job很可能出错了，咱们跳过它
                    break
                try:
                    li_list = job_ul.find_elements_by_tag_name("li")
                except selenium.common.exceptions.NoSuchElementException as e:
                    break

                for li in li_list:
                    try:
                        # li.click() 有可能会失败，如果发生这种情况，是glassdoor网页崩了，应该重新跑这个任务
                        li.click()
                        driver.implicitly_wait(time_limit)

                        # 抓小广告，关了去
                        driver.implicitly_wait(0)  # 如果不设成0,会等time_limit时间的小广告
                        try:
                            ad_div = driver.find_element_by_xpath("""//div[@id="JAModal"]/div""")
                        except selenium.common.exceptions.NoSuchElementException as e:
                            ad_div = None

                        if ad_div:
                            # 如果不是隐藏的广告，关闭之
                            ad_div_class = ad_div.get_attribute("class")
                            if not ad_div_class.__contains__("hidden"):
                                ad_close_tab = driver.find_element_by_xpath("""//*[@id="JAModal"]/div/div[2]/div[1]""")
                                ad_close_tab.click()

                        driver.implicitly_wait(time_limit)

                        job_id = li.get_attribute("data-id")
                        job_title = li.get_attribute("data-normalize-job-title")
                        employer_id = li.get_attribute("data-emp-id")
                        job_location = li.get_attribute("data-job-loc")
                        try:
                            company_logo = li.find_element_by_tag_name("img")
                            company_logo_url = company_logo.get_attribute("data-original-2x")
                        except Exception as e:
                            logging.log(logging.INFO, "没有找到company logo，跳过吧" + str(e))
                            continue

                        driver.implicitly_wait(time_limit)

                        # 如果不能获取公司名称，说明这个glassdoor网页有问题，这份工作跳过不管了
                        try:
                            employer_wrapper_tag = driver.find_element_by_xpath(
                                """//*[@id="HeroHeaderModule"]/div[contains(@class, 'empWrapper')]""")
                        except selenium.common.exceptions.StaleElementReferenceException as e:
                            continue

                        try:
                            employer_wrapper_html = employer_wrapper_tag.get_attribute('innerHTML')
                        except selenium.common.exceptions.StaleElementReferenceException as e:
                            continue
                        employer_wrapper_soup = BeautifulSoup(employer_wrapper_html, "html.parser")
                        company_name = employer_wrapper_soup.find('a', attrs={"class": "empDetailsLink"}).text

                        # get the posted date of a job, if the job have the attribute, 找这个元素不需要等
                        driver.implicitly_wait(0)
                        try:
                            # crawled post_time structure: n days ago
                            post_time_tag = li.find_element_by_xpath(""".//span[contains(@class, 'minor')]""")
                        except selenium.common.exceptions.NoSuchElementException as e:
                            post_time_tag = None

                        posted_time = None
                        if post_time_tag:
                            # days_ago = post_time_tag.text.split()[0]
                            # if days_ago == "Today":
                            #     days_ago = 1
                            # else:
                            #     days_ago = int(days_ago)
                            # posted_time = datetime.now() - timedelta(days=days_ago)
                            posted_time = post_time_tag.text

                        driver.implicitly_wait(time_limit)
                        # try:
                        #     job_tag = driver.find_element_by_xpath(
                        #         """//*[@id="Details"]/div[2]/header//div[contains(@class, 'scrollableTabs')]//span[contains(text(), 'Job')]""")
                        # except selenium.common.exceptions.NoSuchElementException as e:
                        #     continue
                        # else:
                        #     try:
                        #         job_tag.click()
                        #     except selenium.common.exceptions.StaleElementReferenceException as e:
                        #         continue
                        try:
                            job_description_container = driver.find_element_by_xpath(
                                """//*[@id="JobDescriptionContainer"]""")
                            description_div = job_description_container.find_element_by_class_name(
                                "jobDescriptionContent")
                            job_description = description_div.text
                            job_description_html = description_div.get_attribute('innerHTML')
                        except Exception as e:
                            logging.log(logging.INFO, "job_description没找到:" + str(e))
                            continue
                        # job_soup = BeautifulSoup(job_description_html, "html.parser")
                        # job_description_html = job_soup.content

                        # 开始填充job_dict，准备插入到数据库
                        job_info_dict = {}
                        job_info_dict['job_id'] = job_id.strip()
                        job_info_dict['job_title'] = job_title.strip()
                        job_info_dict['company_id'] = employer_id.strip()
                        job_info_dict['location'] = job_location.strip()
                        job_info_dict['job_description'] = job_description
                        job_info_dict['job_description_html'] = job_description_html
                        job_info_dict['headhunter_id'] = None
                        if posted_time:
                            job_info_dict['posted_time'] = posted_time.strip()

                        # crawl its company infomation
                        company_info_dict = dict()
                        company_info_dict["company_id"] = employer_id.strip()
                        company_info_dict["company_name"] = company_name.strip()
                        company_info_dict["logo_url"] = company_logo_url
                        company_website_url = None

                        driver.implicitly_wait(1)  # this should be quick
                        try:
                            company_tag = driver.find_element_by_xpath(
                                """//*[@id="Details"]/div[2]/header//div[contains(@class, 'scrollableTabs')]//span[contains(text(), 'Company')]""")
                        except selenium.common.exceptions.NoSuchElementException as e:
                            company_tag = None

                        if company_tag:
                            try:
                                company_tag.click()
                            except Exception as e:
                                logging.log(logging.INFO, "company标签不让点," + str(e))
                                continue
                            try:
                                basic_info_div = driver.find_element_by_xpath("""//*[@id="EmpBasicInfo"]""")
                                info_entities = basic_info_div.find_elements_by_xpath(
                                    """//div[contains(@class, 'infoEntity')]""")
                            except Exception as e:
                                logging.log(logging.INFO, "company具体信息找不到，跳过," + str(e))
                                continue
                            for entity in info_entities:
                                label = entity.find_element_by_tag_name("label")
                                span = entity.find_element_by_tag_name("span")
                                key = label.text.strip()
                                value = span.text.strip()
                                company_info_dict[key] = value
                            try:
                                company_website_tag = basic_info_div.find_element_by_xpath(""".//a[@class='link']""")
                            except selenium.common.exceptions.NoSuchElementException as e:
                                company_website_tag = None
                            if company_website_tag:
                                company_website_url = company_website_tag.get_attribute("href")
                                company_info_dict["website"] = company_website_url.strip()

                        # try:
                        #     salary_tag = driver.find_element_by_xpath(
                        #         """//*[@id="Details"]/div[2]/header//div[contains(@class, 'scrollableTabs')]//span/[contains(text(), 'Salary')]""")
                        # except selenium.common.exceptions.NoSuchElementException as e:
                        #     salary_tag = None
                        # if salary_tag:
                        #     salary_tag.click()
                        #     driver.implicitly_wait(1)
                        # print(company_info)

                        # 將爬取到的company信息和job信息存入数据库
                        try:
                            conn.insert_one_row_by_dict("company_data_unclean", company_info_dict)
                        except (OperationalError, IntegrityError) as e:
                            logging.log(logging.INFO, str(e))
                        else:
                            print("成功插入一条company", company_info_dict)

                        # 将job信息插入数据库,错了就跳过这个job，不要了
                        try:
                            conn.insert_one_row_by_dict("job_data_unclean", job_info_dict)
                        except (OperationalError, IntegrityError) as e:
                            logging.log(logging.INFO, str(e))
                        #     print("已经存在", job_info_dict)
                        #     continue
                        else:
                            print("成功插入一条job", job_info_dict['job_id'], job_info_dict['job_title'])

                    except Exception as e:
                        print("该工作有问题，跳到下一个" + str(e))

                # 如果有下一页 我们就翻到下一页去
                try:
                    next_page = driver.find_element_by_xpath("""//*[@id="FooterPageNav"]/div/ul/li[7]/a""")
                except Exception as e:
                    next_page = None  # this mean we do not have next_page
                if next_page:
                    try:
                        next_page.click()
                    except Exception as e:
                        break
                    driver.implicitly_wait(time_limit)
                else:
                    break
            except Exception as e:
                print("这页有问题,去下一页了" + str(e))


if __name__ == '__main__':
    with open(job_list_file, "r") as f:
        lines = f.readlines()
        lines = [x.strip() for x in lines]
        for line in lines:
            job_list.append(line)
            line = f.readline()

    # 指定从某一个offset开始爬取
    job_list_offset = 16
    job_list = job_list[job_list_offset:]

    pool_size = 1
    pool = multiprocessing.Pool(pool_size)
    total_num_job_titles = len(job_list)
    one_thread_task = total_num_job_titles // 4

    job_divisions = []
    for i in range(pool_size):
        if i == 0:
            start = 0
        else:
            start = i * one_thread_task

        if i == pool_size:
            end = one_thread_task
        else:
            end = (i + 1) * one_thread_task

        division = job_list[int(start):int(end)]
        job_divisions.append(division)

    processes = []
    for i in range(pool_size):
        pro = Process(target=crawl_bunch_of_job, args=(job_divisions[i], i), daemon=False)
        processes.append(pro)
        pro.start()

    for i in range(pool_size):
        processes[i].join()
