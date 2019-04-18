from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, UserUpdateForm, SeekerUpdateForm, HHUpdateForm
from django.db import connection
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


def register(request):
    with connection.cursor() as cursor:
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                # form.save()
                # username = form.cleaned_data.get('username')
                email = form.cleaned_data.get('email')
                username = form.cleaned_data['username']
                realname = form.cleaned_data['realname']
                usertype = form.cleaned_data['usertype']
                password = form.cleaned_data.get('password1')

                query1 = """INSERT INTO user (email, username, realname, usertype) VALUES ('%s', '%s', '%s', '%s')""" % (
                    email, username, realname, usertype)
                cursor.execute(query1)
                query2 = "SELECT user_id FROM user WHERE username = '%s'" % username
                cursor.execute(query2)
                uid = cursor.fetchone()

                str1 = "{0}".format(usertype)
                if str1 == "0":
                    query3 = "INSERT INTO jobseeker (user_id) VALUES ('%s')" % uid
                    cursor.execute(query3)
                else:
                    query3 = "INSERT INTO headhunter (user_id) VALUES ('%s')" % uid
                    cursor.execute(query3)

                User.objects.create_user(username, email, password)
                return redirect("login")
        else:
            form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    with connection.cursor() as cursor:
        if request.method == 'POST':
            query = "SELECT usertype FROM user WHERE username = '%s'" % request.user.username
            previous_name = request.user.username
            cursor.execute(query)
            usertype = cursor.fetchone()
            str1 = "{0}".format(usertype)
            type_str = str1[1:str1.__len__() - 2]
            if type_str == "0":
                u_form = UserUpdateForm(request.POST, instance=request.user)
                p_form = SeekerUpdateForm(request.POST,
                                          request.FILES,
                                          instance=request.user.profile)

                if u_form.is_valid() and p_form.is_valid():
                    username = u_form.cleaned_data.get('username')
                    email = u_form.cleaned_data.get('email')
                    query1 = "UPDATE user SET username = '%s', email = '%s' WHERE username = '%s'" % (
                    username, email, previous_name)
                    print(username)
                    print(request.user.username)
                    cursor.execute(query1)
                    query2 = "SELECT user_id FROM user WHERE username = '%s'" % username
                    cursor.execute(query2)
                    uid = cursor.fetchone()
                    str2 = "{0}".format(uid)
                    uid_str = str2[1:str2.__len__() - 2]

                    major = p_form.cleaned_data['major']
                    gpa = p_form.cleaned_data['GPA']
                    university = p_form.cleaned_data['university']
                    graduation = p_form.cleaned_data['graduation']
                    salary = p_form.cleaned_data['salary']
                    personal_summary = p_form.cleaned_data['personal_summary']
                    query3 = "UPDATE jobseeker SET major = '%s', GPA = '%s', university = '%s', graduation_date = '%s'" \
                             ", salary_expectation = '%s', personal_summary = '%s' WHERE user_id = %s" % (
                             major, gpa, university, graduation, salary, personal_summary, uid_str)
                    cursor.execute(query3)

                    u_form.save()
                    p_form.save()
                    return redirect('profile')

            else:
                u_form = UserUpdateForm(request.POST, instance=request.user)
                p_form = HHUpdateForm(request.POST,
                                      request.FILES,
                                      instance=request.user.profile)

                if u_form.is_valid() and p_form.is_valid():
                    username = u_form.cleaned_data.get('username')
                    email = u_form.cleaned_data.get('email')
                    query1 = "UPDATE user SET username = '%s', email = '%s' WHERE username = '%s'" % (
                        username, email, previous_name)
                    cursor.execute(query1)
                    query2 = "SELECT user_id FROM user WHERE username = '%s'" % username
                    cursor.execute(query2)
                    uid = cursor.fetchone()
                    str2 = "{0}".format(uid)
                    uid_str = str2[1:str2.__len__() - 2]

                    synopsis = p_form.cleaned_data['synopsis']
                    occupation = p_form.cleaned_data['occupation']
                    query3 = "UPDATE headhunter SET synopsis = '%s', occupation_direction = '%s' WHERE user_id = '%s'" % (
                        synopsis, occupation, uid_str)
                    cursor.execute(query3)

                    u_form.save()
                    p_form.save()
                    return redirect('profile')

        else:
            query = "SELECT usertype FROM user WHERE username = '%s'" % request.user.username
            cursor.execute(query)
            usertype = cursor.fetchone()
            str1 = "{0}".format(usertype)
            type_str = str1[1:str1.__len__() - 2]
            if type_str == "0":
                u_form = UserUpdateForm(instance=request.user)
                p_form = SeekerUpdateForm(instance=request.user.profile)
            else:
                u_form = UserUpdateForm(instance=request.user)
                p_form = HHUpdateForm(instance=request.user.profile)

        context = {
            'u_form': u_form,
            'p_form': p_form
        }

    return render(request, 'users/userprofile.html', context)
