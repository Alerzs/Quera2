from django.db import models
from django.contrib.auth.models import AbstractUser

class QueraUser(AbstractUser):
    name = models.CharField(max_length=25)
    phone = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.username
