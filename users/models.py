from django.db import models
from PIL import Image
from django.contrib.auth.models import User


class Profile(models.Model):
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pic')
    major = models.CharField(default='none', max_length=50)
    GPA = models.FloatField(default=0.0)
    university = models.CharField(default='none', max_length=100)
    graduation = models.CharField(default='1', choices=GRAD_CHOICES, max_length=1)
    salary = models.CharField(default='A', choices=SALARY_CHOICES, max_length=1)
    personal_summary = models.CharField(default='none', max_length=1500)
    synopsis = models.CharField(default='none', max_length=2000)
    occupation = models.CharField(default='none', max_length=2000)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, **kwargs):
        super().save()

        pic = Image.open(self.image.path)

        if pic.height > 350 or pic.width > 350:
            result_size = (350, 350)
            pic.thumbnail(result_size)
            pic.save(self.image.path)
