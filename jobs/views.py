from django.shortcuts import render, redirect, HttpResponse
from django.db import connection
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import JobPostForm
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView
)
from .models import Post

@login_required
def post_job(request):
    with connection.cursor() as cursor:
        query1 = "SELECT usertype FROM user WHERE username = '%s'" % request.user.username
        cursor.execute(query1)
        usertype = cursor.fetchone()
        str1 = "{0}".format(usertype)
        type_str = str1[1:str1.__len__() - 2]
        if type_str == "1":
            if request.method == 'POST':
                j_form = JobPostForm(request.POST, instance=request.user)
                if j_form.is_valid():
                    job_title = j_form.cleaned_data['job_title']
                    salary = j_form.cleaned_data['salary']
                    location = j_form.cleaned_data['location']
                    job_description = j_form.cleaned_data['job_description']
                    query2 = "SELECT user_id FROM user WHERE username = '%s'" % request.user.username
                    cursor.execute(query2)
                    uid = cursor.fetchone()
                    str2 = "{0}".format(uid)
                    uid_str = str2[1:str2.__len__() - 2]
                    query3 = "INSERT INTO job (job_title, salary, location, job_description, headhunter_id) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')".format(job_title, salary, location, job_description, uid_str)
                    cursor.execute(query3)
                    p = Post(job_title=job_title, salary=salary, location=location, job_description=job_description, author=request.user)
                    p.save()
                    #message
                    return redirect('profile')
            else:
                j_form = JobPostForm()
            return render(request, 'jobs/postjob.html', {'form': j_form})
        else:
            return redirect('jobsite-home')

@login_required
def see_posted(request):
    with connection.cursor() as cursor:
        query1 = "SELECT usertype FROM user WHERE username = '%s'" % request.user.username
        cursor.execute(query1)
        usertype = cursor.fetchone()
        str1 = "{0}".format(usertype)
        type_str = str1[1:str1.__len__() - 2]
        if type_str == "1":
            query2 = "SELECT user_id FROM user WHERE username = '%s'" % request.user.username
            cursor.execute(query2)
            uid = cursor.fetchone()
            str2 = "{0}".format(uid)
            uid_str = str2[1:str2.__len__() - 2]
            query3 = "SELECT * FROM job WHERE headhunter_id = '%s'" % uid_str
            cursor.execute(query3)
            result = cursor.fetchall()
            if request.method == 'POST':
                search_text = request.POST.get('textfield', None)
                query4 = "DELETE FROM job WHERE job_id = {0}".format(search_text)
                print(query4)
                cursor.execute(query4)
                return render(request, 'jobs/userjob.html')
            return render(request, 'jobs/userjob.html', {'results': result})

        else:
            #message
            return redirect('jobsite-home')



def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'jobs/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'jobs/job_list.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']


class PostDetailView(DetailView):
    model = Post
    template_name = 'jobs/job_detail.html'


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
