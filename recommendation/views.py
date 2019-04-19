from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.template.loader import get_template
from django.db import connection
from Shortest_job_first import settings
import smtplib
from django.http.response import HttpResponse
from datetime import datetime
import datetime
from . import similarity_calculation
from typing import List, Dict


def send_email(uid: str, job_list: List[Dict]):
    with connection.cursor() as cursor:
        plaintext = get_template('email_template.txt')
        htmltext = get_template('email_template.html')
        print(type(htmltext))
        print(htmltext)

        query1 = f"""SELECT username, email FROM user WHERE user_id = '{uid}'"""
        cursor.execute(query1)
        row = cursor.fetchone()
        username: str = row[0]

        dict_to_pass = {'username': username,
                        'job1': job_list[0],
                        'job2': job_list[1],
                        'job3': job_list[2],
                        'job4': job_list[3],
                        'job5': job_list[4],
                        'job6': job_list[5],}
        text_content = plaintext.render(dict_to_pass)
        html_content = htmltext.render(dict_to_pass)

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)

        # Authentication
        server.login("team309host@gmail.com", "cs4112019")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"""{username}- Thank you for dropping by!"""
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = row[1]

        message1 = MIMEText(text_content, 'plain')
        message2 = MIMEText(html_content, 'html')
        msg.attach(message1)
        msg.attach(message2)
        server.send_message(msg)
        server.quit()


#send email logic
def email_sending_gate(request):
    with connection.cursor() as cursor:
        query = "SELECT usertype FROM user WHERE username = '%s'" % request.user.username
        cursor.execute(query)
        usertype = cursor.fetchone()
        str1 = "{0}".format(usertype)
        type_str = str1[1:str1.__len__() - 2]
        if type_str == "1":
            print("exit1")
            return HttpResponse('')
        else:
            #if just recommended one day ago, do not recommend this time
            uid = get_uid(request.user.username)
            query1 = f"""SELECT last_recommend_time FROM jobseeker WHERE user_id = '{uid}'"""
            cursor.execute(query1)
            result1 = cursor.fetchall()
            last_recommend_time = ""
            for row in result1:
                last_recommend_time = row[0]
            if not last_recommend_time:
                lastdate = datetime.datetime.strptime("2000-01-01", '%Y-%m-%d').date()
            else:
                lastdate = last_recommend_time
            thisdate = datetime.date.today()
            if (thisdate - lastdate).days <= 1:
                print("exit2")
                return HttpResponse('')
            else:
                print("exit3")
                #check if enough for fetch
                query6 = f"""SELECT count(*) FROM behavior_job WHERE user_id = '{uid}' AND recommended = 0"""
                cursor.execute(query6)
                row = cursor.fetchone()
                if row[0] < 3:
                    updatequery1 = f"""UPDATE behavior_job SET recommended = 0 WHERE user_id = '{uid}'"""
                    cursor.execute(updatequery1)

                query7 = f"""SELECT count(*) FROM interest_job WHERE user_id = '{uid}' AND recommended = 0"""
                cursor.execute(query7)
                row1 = cursor.fetchone()
                if row1[0] < 3:
                    updatequery2 = f"""UPDATE interest_job SET recommended = 0 WHERE user_id = '{uid}'"""
                    cursor.execute(updatequery2)

                #start fetching
                query2 = f"""SELECT job_id, job_title, company_name, location, job_description FROM ((SELECT job_id FROM interest_job WHERE user_id = '{uid}' AND recommended = 0 LIMIT 3) as atable natural join job) inner join company on job.company_id = company.company_id LIMIT 3"""
                cursor.execute(query2)
                result2 = cursor.fetchall()
                datalist = []
                for row in result2:
                    # pass to email template using dict
                    one_row_dict = {'job_title': row[1],
                                    'company_name': row[2],
                                    'location': row[3],
                                    'job_description': (row[4])[:500],}
                    datalist.append(one_row_dict)
                    query4 = f"""UPDATE interest_job SET recommended = 1 WHERE job_id = '{row[0]}'"""
                    cursor.execute(query4)

                query3 = f"""SELECT job_id, job_title, company_name, location, job_description FROM ((SELECT job_id FROM behavior_job WHERE user_id = '{uid}' AND recommended = 0 LIMIT 3) as atable natural join job) inner join company on job.company_id = company.company_id LIMIT 3"""
                cursor.execute(query3)
                result3 = cursor.fetchall()
                for row in result3:
                    one_row_dict = {'job_title': row[1],
                                    'company_name': row[2],
                                    'location': row[3],
                                    'job_description': (row[4])[:500], }
                    datalist.append(one_row_dict)
                    query5 = f"""UPDATE behavior_job SET recommended = 1 WHERE job_id = '{row[0]}'"""
                    cursor.execute(query5)

                updatetime = f"""UPDATE jobseeker SET last_recommend_time = CURDATE() WHERE user_id = '{uid}'"""
                cursor.execute(updatetime)

                print(datalist)
                send_email(uid, datalist)
                return HttpResponse('')



#possible - personal summary parser/combinator logic



def get_uid(username: str):
    with connection.cursor() as cursor:
        query = "SELECT user_id FROM user WHERE username = '%s'" % username
        cursor.execute(query)
        uid = cursor.fetchone()
        str2 = "{0}".format(uid)
        uid_str = str2[1:str2.__len__() - 2]
        return uid_str
