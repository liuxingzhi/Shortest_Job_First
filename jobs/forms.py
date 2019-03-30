
from django import forms
from django.contrib.auth.models import User

class JobPostForm(forms.ModelForm):
    job_title = forms.CharField(max_length=100, label='Job Title')
    salary = forms.CharField(max_length=50, label='Estimated Salary')
    location = forms.CharField(max_length=50, label='Location')
    job_description = forms.CharField(max_length=20000, label='Job Description')
    #job_description_html = forms.CharField(max_length=20000, label='Job Description HTML')

    class Meta:
        model = User
        fields = ['job_title', 'salary', 'location', 'job_description']
