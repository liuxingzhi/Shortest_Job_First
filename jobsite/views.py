from django.shortcuts import render
from django.shortcuts import render
from datetime import datetime
from django.http.response import HttpResponse, JsonResponse, FileResponse, Http404
from django.views.decorators.http import require_http_methods
import os, json
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection
import django
from django.contrib.auth.models import User


# Create your views here.
@require_http_methods(["GET"])
def homeproc(request):
    return render(request, "jobsite/index.html")


def career(request):
    return render(request, "jobsite/career.html")


def tips(request):
    return render(request, "jobsite/tips.html")


def gpa(request):
    return render(request, "jobsite/gpa.html")


def resume(request):
    return render(request, "jobsite/resume.html")


def programming(request):
    return render(request, "jobsite/programming.html")


def top(request):
    return render(request, "jobsite/top.html")


def job_search(request):
    if request.method == "GET":
        return render(request, "jobsite/career.html")

    # print("I am here")
    job_title: str = request.POST.get('job_title', "")
    location: str = request.POST.get('location', "")
    company_name: str = request.POST.get('company_name', "")
    industry: str = request.POST.get('industry', "")
    maximum_job_return = 50
    with connection.cursor() as cursor:
        sql = f'''select * from job as j
        inner join company as c
        on c.company_id = j.company_id
        where lower(j.job_title) like "%{job_title}%"
        and j.location like "%{location}%"
        and c.company_name like "%{company_name}%"
        and c.industry like "%{industry}%" 
        order by j.job_id, j.location, c.industry, c.company_id asc
        limit {maximum_job_return}'''
        cursor.execute(sql)
        result = cursor.fetchall()

    datalist = []
    for row in result:
        one_row_dict = {}
        for description_tuple, value in zip(cursor.description, row):
            one_row_dict[description_tuple[0]] = value
        datalist.append(one_row_dict)

    return render(request, "jobsite/career.html",  {"data_list": datalist})


def job_info(request, job_id):
    pass


def company_info(request, company_id):
    pass


def add_favorite_job(request, job_id):
    pass


def show_favorite_job(request, user_id):
    pass

def timer_start(request):
    with connection.cursor() as cursor:
        print("entered view timer_start")
        start_time = request.GET.get('start')
        job_id = request.GET.get('job_id')
        uid = get_uid(request.user.username)
        query = f"""insert into browse_time (job_id, user_id, start_time, end_time) values('{job_id}', '{uid}', '{start_time}', '0') """
        cursor.execute(query)
        return HttpResponse('')


def timer_end(request):
    with connection.cursor() as cursor:
        print("entered view timer_end")
        end_time = request.GET.get('end')
        job_id = request.GET.get('job_id')
        uid = get_uid(request.user.username)
        query1 = f"""UPDATE browse_time SET end_time = '{end_time}' WHERE job_id = '{job_id}' AND user_id = '{uid}' AND end_time = '0'"""
        cursor.execute(query1)
        query2 = f"""UPDATE browse_time SET time_elapsed = end_time - start_time WHERE job_id = '{job_id}' AND user_id = '{uid}' AND end_time = '{end_time}'"""
        cursor.execute(query2)
        return HttpResponse('')


def search_content_saver(request):
    with connection.cursor() as cursor:
        print("entered view saver")
        search_time = request.GET.get('time')
        job_title = request.GET.get('job_title')
        company_name = request.GET.get('company_name')
        industry = request.GET.get('industry')
        location = request.GET.get('location')
        uid = get_uid(request.user.username)
        query = f"""insert into search_history (user_id, search_time, job_title, company_name, industry, location) values('{uid}', '{search_time}', '{job_title}', '{company_name}', '{industry}', '{location}') """
        cursor.execute(query)
        return HttpResponse('')


def get_uid(username: str):
    with connection.cursor() as cursor:
        query = "SELECT user_id FROM user WHERE username = '%s'" % username
        cursor.execute(query)
        uid = cursor.fetchone()
        str2 = "{0}".format(uid)
        uid_str = str2[1:str2.__len__() - 2]
        return uid_str