from django.db import models
from PIL import Image


# Create your models here.
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    real_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    nickname = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'user'


class Favorite(models.Model):
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    user = models.ForeignKey('Jobseeker', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'favorite'


class Headhunter(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, unique=True)
    synopsis = models.CharField(max_length=500)
    occupation_direction = models.CharField(max_length=500)

    class Meta:
        managed = False
        db_table = 'headhunter'


class Company(models.Model):
    company_id = models.CharField(primary_key=True, max_length=100)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    headquarters = models.CharField(max_length=200, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=100, blank=True, null=True)
    revenue = models.CharField(max_length=100, blank=True, null=True)
    website = models.CharField(max_length=200, blank=True, null=True)
    founded = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    competitors = models.CharField(max_length=500, blank=True, null=True)
    logo_path = models.CharField(max_length=300, blank=True, null=True)
    logo_url = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'company'


class CompanyDataUnclean(models.Model):
    company_id = models.CharField(primary_key=True, max_length=100)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    headquarters = models.CharField(max_length=200, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=100, blank=True, null=True)
    revenue = models.CharField(max_length=100, blank=True, null=True)
    website = models.CharField(max_length=200, blank=True, null=True)
    founded = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    competitors = models.CharField(max_length=500, blank=True, null=True)
    logo_path = models.CharField(max_length=300, blank=True, null=True)
    logo_url = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'company_data_unclean'


class Job(models.Model):
    job_id = models.CharField(primary_key=True, max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False, null=False)
    salary = models.CharField(max_length=100, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    job_description = models.CharField(max_length=27000, blank=True, null=True)
    job_description_html = models.CharField(max_length=33000, blank=True, null=True)
    posted_time = models.CharField(max_length=100, blank=True, null=True)
    headhunter = models.ForeignKey(Headhunter, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'job'


class JobDataUnclean(models.Model):
    job_id = models.CharField(primary_key=True, max_length=100)
    company = models.ForeignKey(CompanyDataUnclean, on_delete=models.CASCADE, blank=True, null=True)
    salary = models.CharField(max_length=100, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    job_description = models.CharField(max_length=27000, blank=True, null=True)
    job_description_html = models.CharField(max_length=33000, blank=True, null=True)
    posted_time = models.CharField(max_length=100, blank=True, null=True)
    headhunter = models.ForeignKey(Headhunter, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'job_data_unclean'


class Jobseeker(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, unique=True)
    major = models.CharField(max_length=100)
    gpa = models.FloatField(db_column='GPA', blank=True, null=True)  # Field name made lowercase.
    university = models.CharField(max_length=100, blank=True, null=True)
    graduation_date = models.DateField(blank=True, null=True)
    salary_expectation = models.FloatField(blank=True, null=True)
    personal_summary = models.CharField(max_length=1500, blank=True, null=True)
    last_recommend_time = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jobseeker'


class JobseekerTags(models.Model):
    user = models.ForeignKey(Jobseeker, on_delete=models.CASCADE)
    tag = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'jobseeker_tags'


class JobTags(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    tag = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'job_tags'
