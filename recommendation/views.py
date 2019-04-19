from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.template.loader import get_template
from django.db import connection
from Shortest_job_first import settings
import smtplib


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
        msg['To'] = 'team309host@gmail.com'
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


def weight_adder(job_str : str, uid: str):
    with connection.cursor() as cursor:
        query1 = f"""SELECT search_keyword, count FROM sh_counter WHERE user_id = '{uid}'"""
        cursor.execute(query1)
        result = cursor.fetchall()
        total_weight = 0
        for row in result:
            if row[0] in job_str:
                total_weight += row[1]
        return total_weight


def get_by_browse_time(threshold: int, uid: str):
    with connection.cursor() as cursor:
        query1 = f"""SELECT job_title, company_name, industry, location FROM (((SELECT DISTINCT job_id FROM browse_time WHERE user_id = '{uid}' AND time_elapsed >= {threshold}) as atable natural join job) natural join company)"""
        cursor.execute(query1)
        return cursor.fetchall()

# def extract_search_history(request):
#     with connection.cursor() as cursor:
#         uid = get_uid(request.user.username)
#         query1 = f"""SELECT DISTINCT job_title FROM search_history WHERE user_id = '{uid}'"""
#         query2 = f"""SELECT DISTINCT company_name FROM search_history WHERE user_id = '{uid}'"""
#         query3 = f"""SELECT DISTINCT industry FROM search_history WHERE user_id = '{uid}'"""
#         query4 = f"""SELECT DISTINCT location FROM search_history WHERE user_id = '{uid}'"""
#         result = esh_wrapper(query1) + esh_wrapper(query2) + esh_wrapper(query3) + esh_wrapper(query4)
#         extract_personal_summary()
#         print(result)
#         return render(request, "jobsite/index.html")
#
#
# def esh_wrapper(query: str):
#     with connection.cursor() as cursor:
#         cursor.execute(query)
#         result1 = cursor.fetchall()
#         str1 = "{0}".format(result1)
#         to_append = str1.replace("(", "").replace(")", "").replace(",", " ").replace("'", "").replace("  ", " ")
#         return to_append


def get_uid(username: str):
    with connection.cursor() as cursor:
        query = "SELECT user_id FROM user WHERE username = '%s'" % username
        cursor.execute(query)
        uid = cursor.fetchone()
        str2 = "{0}".format(uid)
        uid_str = str2[1:str2.__len__() - 2]
        return uid_str
