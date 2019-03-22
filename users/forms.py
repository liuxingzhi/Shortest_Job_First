from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    realname = forms.CharField(min_length=2, max_length=30, label="Real Name")
    usertype = forms.IntegerField(required=0, max_value=1, min_value=0)  # 0:jobseeker, 1:headhunter


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
    major = forms.CharField(max_length=50)
    GPA = forms.FloatField(max_value=4, min_value=0)
    university = forms.CharField(max_length=100)
    graduation = forms.ChoiceField(choices=GRAD_CHOICES)
    salary = forms.ChoiceField(choices=SALARY_CHOICES)

    class Meta:
        model = Profile
        fields = ['image', 'major', 'GPA', 'university', 'graduation', 'salary']


class HHUpdateForm(forms.ModelForm):
    synopsis = forms.CharField()
    occupation = forms.CharField()

    class Meta:
        model = Profile
        fields = ['image', 'synopsis', 'occupation']
