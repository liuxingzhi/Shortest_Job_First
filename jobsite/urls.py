from django.urls import path, re_path
from . import views
from users import views as user_views

urlpatterns = [
    path("", views.homeproc, name = "jobsite-home"),
    path("register/", user_views.register, name = "register"),
]
