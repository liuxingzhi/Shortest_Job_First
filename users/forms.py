from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    realname = forms.CharField(min_length=2, max_length=30, label="Real Name")
    SALARY_CHOICES = (
        ('0', "I'm looking for a job"),
        ('1', "I am a headhunter, and I want to post jobs"),
    )
    usertype = forms.ChoiceField(choices=SALARY_CHOICES, label='What services are you looking for?')  # 0:jobseeker, 1:headhunter


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class SeekerUpdateForm(forms.ModelForm):
    SALARY_CHOICES = (
        ('A', '$0~$3000'),
        ('B', '$3000~$6000'),
        ('C', '$6000~$10000'),
        ('D', '$10000~'),
    )
    GRAD_CHOICES = (
        ('1', '2019'),
        ('2', '2020'),
        ('3', '2021'),
        ('4', '2022'),
    )
    major = forms.CharField(max_length=50, label='Major')
    GPA = forms.FloatField(max_value=4, min_value=0, label='Current GPA')
    university = forms.CharField(max_length=100, label='University')
    graduation = forms.ChoiceField(choices=GRAD_CHOICES, label='Year of graduation')
    salary = forms.ChoiceField(choices=SALARY_CHOICES, label='Salary Expectation')

    class Meta:
        model = Profile
        fields = ['image', 'major', 'GPA', 'university', 'graduation', 'salary']
        labels = {
            'image': 'Choose an image for your profile'
        }


class HHUpdateForm(forms.ModelForm):
    synopsis = forms.CharField(label='Synopsis')
    occupation = forms.CharField(label='Occupation direction')

    class Meta:
        model = Profile
        fields = ['image', 'synopsis', 'occupation']
        labels = {
            'image': 'Choose an image for your profile'
        }
