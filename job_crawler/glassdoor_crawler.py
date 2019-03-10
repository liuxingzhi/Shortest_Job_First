import selenium
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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

glassdoor_main_url = "https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=software&sc.keyword=software&locT=&locId=&jobType="
time_limit = 15
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


def crawl_one_job_title(job: str):
    # go to the main page of glassdoor
    driver.get(glassdoor_main_url)
    driver.implicitly_wait(time_limit)
    keyword = driver.find_element_by_id("sc.keyword")
    keyword.clear()
    keyword.send_keys(job)
    location = driver.find_element_by_id("sc.location")
    location.clear()
    driver.find_element_by_id("HeroSearchButton").click()

    for i in range(20):
        job_ul = driver.find_element_by_xpath("""//*[@id="MainCol"]/div/ul""")
        li_list = job_ul.find_elements_by_tag_name("li")
        for li in li_list:
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
            employer_id = li.get_attribute("data-emp-id")
            job_location = li.get_attribute("data-job-loc")
            company_name = driver.find_element_by_xpath(
                """//*[@id="HeroHeaderModule"]/div[3]/div[3]/a[contains(@class, 'empDetailsLink')]""").text
            # get the posted date of a job, if the job have the attribute
            try:
                # crawled post_time structure: n days ago
                post_time_tag = li.find_element_by_xpath("""//span[contains(@class, 'minor')]""")
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

            job_description_container = driver.find_element_by_xpath("""//*[@id="JobDescriptionContainer"]""")
            description_div = job_description_container.find_element_by_class_name("jobDescriptionContent")
            job_description = description_div.text
            job_description_html = description_div.get_attribute('innerHTML')

            # crawl its company infomation
            company_info = dict()
            company_info["company_id"] = employer_id
            company_info["company_name"] = company_name
            company_website_url = None

            driver.implicitly_wait(1) # this should be quick
            try:
                company_tag = driver.find_element_by_xpath(
                    """//*[@id="Details"]/div[2]/header//div[contains(@class, 'scrollableTabs')]//span[contains(text(), 'Company')]""")
            except selenium.common.exceptions.NoSuchElementException as e:
                company_tag = None

            if company_tag:
                company_tag.click()
                basic_info_div = driver.find_element_by_xpath("""//*[@id="EmpBasicInfo"]""")
                info_entities = basic_info_div.find_elements_by_xpath(
                    """//div[contains(@class, 'infoEntity')]""")
                for entity in info_entities:
                    label = entity.find_element_by_tag_name("label")
                    span = entity.find_element_by_tag_name("span")
                    key = label.text
                    value = span.text
                    company_info[key] = value
                try:
                    company_website_tag = basic_info_div.find_element_by_xpath("//a[contains(text(), 'Visit']")
                except selenium.common.exceptions.NoSuchElementException as e:
                    company_website_tag = None
                if company_website_tag:
                    company_website_url = company_website_tag.get_attribute("href")
                    company_info["website"] = company_website_url
            # try:
            #     salary_tag = driver.find_element_by_xpath("""//*[@id="Details"]/div[2]/header//div[contains(@class, 'scrollableTabs')]//span/[contains(text(), 'Salary')]""")
            # except selenium.common.exceptions.NoSuchElementException as e:
            #     salary_tag = None
            # if salary_tag:
            #     salary_tag.click()
            #     driver.implicitly_wait(1)
            print(company_info)
        # 如果有下一页 我们就翻到下一页去
        try:
            next_page = driver.find_element_by_xpath("""//*[@id="FooterPageNav"]/div/ul/li[7]/a""")
        except selenium.common.exceptions.NoSuchElementException as e:
            next_page = None  # this mean we do not have next_page
        if next_page:
            next_page.click()
            driver.implicitly_wait(time_limit)
        else:
            break


if __name__ == '__main__':
    with open(job_list_file, "r") as f:
        lines = f.readlines()
        lines = [x.strip() for x in lines]
        for line in lines:
            job_list.append(line)
            line = f.readline()

    chrome_options = Options()
    # chrome_options.add_argument('--headless')# 运行时关闭窗口
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

    # sign_in()
    for job in job_list:
        crawl_one_job_title(job)

    driver.quit()
