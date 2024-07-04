from django.db import models
from user.models import User

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.user.name

class Vehicle(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    model = models.CharField(max_length=255)
    number = models.CharField(max_length=20)

    def __str__(self):
        return self.model
