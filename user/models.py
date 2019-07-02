from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Meta:
        db_table = 'auth_user'

    access_token = models.TextField()
    fb_user_id = models.CharField(max_length=100)
