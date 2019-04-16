from django.urls import path, re_path
from . import views
from users import views as user_views

urlpatterns = [
    path("", views.homeproc),
    re_path(r"^career*", views.career),
    re_path(r"^job_search", views.job_search, name="job_search"),
    re_path(r"^tips", views.tips),
    re_path(r"^gpa", views.gpa),
    re_path(r"^resume", views.resume),
    re_path(r"^programming", views.programming),
    re_path(r"^top", views.top),
    path("ajax/timerstart", views.timer_start),
    path("ajax/timerend", views.timer_end),
]
