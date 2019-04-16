"""Shortest_job_first URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views
from jobsite import views as jobsite_views
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static
from jobs import views as search_views

urlpatterns = [
    path("", jobsite_views.homeproc, name="jobsite-home"),
    path('jobsite/', include('jobsite.urls')),
    path('admin/', admin.site.urls),
    path("register/", user_views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name='users/signin.html'), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name='users/signout.html'), name="logout"),
    path('profile/', user_views.profile, name='profile'),
    path('postjob/', search_views.post_job, name='job-post'),
    path('post/', search_views.PostListView.as_view(), name='job-list'),
    path('post/<int:pk>/', search_views.PostDetailView.as_view(), name='job-detail'),
    path('post/<int:pk>/delete/', search_views.PostDeleteView.as_view(), name='post-delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
