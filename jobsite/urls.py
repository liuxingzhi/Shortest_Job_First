from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.homeproc),
    re_path(r"^career*", views.career),
    re_path(r"^tips", views.tips),
    re_path(r"^gpa", views.gpa),
    re_path(r"^resume", views.resume),
    re_path(r"^programming", views.programming),
    re_path(r"^top", views.top),
    path("company/<str:company_id>", views.company_info),
    path("job/<str:job_id>", views.job_info),
]
