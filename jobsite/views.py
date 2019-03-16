from django.shortcuts import render
from django.shortcuts import render
from datetime import datetime
from django.http.response import HttpResponse, JsonResponse, FileResponse, Http404
from django.views.decorators.http import require_http_methods
import os, json
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder


# Create your views here.

@require_http_methods(["GET"])
def homeproc(request):
    response = HttpResponse()
    response.write("<h1>This is homepage,more functions are <a href='./msggate'>here</a></h1>")
    response.write("<h2>this is a small title</h2>")
    response.write("<h3>Hello world</h3>")
    return response
