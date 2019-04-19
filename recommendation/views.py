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


def send_email(request):
    with connection.cursor() as cursor:
        plaintext = get_template('email_template.txt')
        htmltext = get_template('email_template.html')
        print(type(htmltext))
        print(htmltext)


        query1 = "SELECT job_description_html FROM job LIMIT 5, 1"
        cursor.execute(query1)
        raw = cursor.fetchall()
        str1 = "{0}".format(raw)
        str2 = str1[3:str1.__len__() - 5]
        str_to_pass = str2.replace(r"\n", '')

        dict_to_pass = {'username': request.user.username,
                        'html_text': str_to_pass}

        subject, from_email, to = f"""{request.user.username} - Thank you for dropping by!""", settings.EMAIL_HOST_USER, 'team309host@gmail.com'
        text_content = plaintext.render(dict_to_pass)
        html_content = htmltext.render(dict_to_pass)
        # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        # msg.attach_alternative(html_content, "text/html")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)

        # Authentication
        server.login("team309host@gmail.com", "cs4112019")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"""{request.user.username}- Thank you for dropping by!"""
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = 'jeff_illini_2017@outlook.com'
        message1 = MIMEText(text_content, 'plain')
        message2 = MIMEText(html_content, 'html')
        msg.attach(message1)
        msg.attach(message2)
        server.send_message(msg)
        server.quit()
        return render(request, "jobsite/index.html")


def search_history_counter(request):
    with connection.cursor() as cursor:
        uid = get_uid(request.user.username)
        shc_wrapper("job_title", uid)
        shc_wrapper("company_name", uid)
        shc_wrapper("industry", uid)
        shc_wrapper("location", uid)
        query1 = f"""UPDATE search_history SET counted = 1 WHERE user_id = '{uid}'"""
        cursor.execute(query1)
        return render(request, "jobsite/index.html")


def shc_wrapper(col: str, uid: str):
    with connection.cursor() as cursor:
        query1 = f"""SELECT {col}, COUNT({col}) as count FROM search_history WHERE user_id = '{uid}' AND {col} <> '' AND counted = 0 GROUP BY {col} ORDER BY count DESC;"""
        cursor.execute(query1)
        result = cursor.fetchall()
        for row in result:
            query2 = f"""INSERT INTO sh_counter (user_id, search_keyword, count) VALUES ('{uid}', '{row[0]}', '{row[1]}') ON DUPLICATE KEY UPDATE count=count+{row[1]}"""
            cursor.execute(query2)


#search history combinator, called when decide to recommend
def search_history_combinator(uid: str):
    with connection.cursor() as cursor:
        query1 = f"""SELECT search_keyword, count FROM sh_counter WHERE user_id = '{uid}'"""
        cursor.execute(query1)
        result = cursor.fetchall()
        to_return: str = ""
        if not result:
            return to_return
        for row in result:
            for i in range(0, row[1]):
                to_return += (" " + row[0])
        return to_return


#send email logic
def email_sending_gate(request):
    with connection.cursor() as cursor:
        query = "SELECT usertype FROM user WHERE username = '%s'" % request.user.username
        cursor.execute(query)
        usertype = cursor.fetchone()
        str1 = "{0}".format(usertype)
        type_str = str1[1:str1.__len__() - 2]
        if type_str == "1":
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
                lastdate = datetime.strptime("2000-01-01", '%Y-%m-%d').date()
            else:
                lastdate = datetime.strptime(last_recommend_time, '%Y-%m-%d').date()
            thisdate = datetime.date.today()
            if (thisdate - lastdate).days <= 1:
                return HttpResponse('')
            else:
                #if not enough personal summary, do not recommend
                query2 = f"""SELECT personal_summary from jobseeker WHERE user_id = '{uid}'"""
                cursor.execute(query2)
                result2 = cursor.fetchone()
                if not all(result2):
                    return HttpResponse('')
                else:
                    #if not enough search history, do not recommend
                    search_history = search_history_combinator(uid)
                    if not search_history:
                        return HttpResponse('')
                    else:
                        #recommend
                        pass



#possible - personal summary parser/combinator logic

#to be deleted
def testing(request):
    uid = get_uid(request.user.username)
    result = get_by_browse_time(15000, uid)
    print(result)
    return render(request, "jobsite/index.html")


#use in query
def get_by_browse_time(threshold: int, uid: str):
    with connection.cursor() as cursor:
        query1 = f"""SELECT job_title, company_name, industry, location FROM 
        (((SELECT job_id, sum(time_elapsed) as total_time FROM browse_time WHERE user_id = '{uid}' 
        GROUP BY job_id HAVING total_time >= {threshold}) as atable natural join job) natural join company)"""
        cursor.execute(query1)
        return cursor.fetchall()


def get_uid(username: str):
    with connection.cursor() as cursor:
        query = "SELECT user_id FROM user WHERE username = '%s'" % username
        cursor.execute(query)
        uid = cursor.fetchone()
        str2 = "{0}".format(uid)
        uid_str = str2[1:str2.__len__() - 2]
        return uid_str
