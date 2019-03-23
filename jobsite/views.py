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


def job_search(request, keyword):
    job_title = str
    location = str
    company_name = str
    industry = str
    with connection.cursor() as cursor:
        sql = f'''select * from job as j
        inner join company as c
        on c.company_id = j.company_id
        where lower(j.job_title) like "%{job_title}%"
        and j.location like BINARY "%{location}%"
        and c.company_name like "%{company_name}%"
        and c.industry like "%{industry}%" 
        order by j.job_id, j.location, c.industry, c.company_id asc'''
        cursor.execute(sql)
        result = cursor.fetchall()


def job_info(request, job_id):
    pass


def company_info(request, company_id):
    pass
