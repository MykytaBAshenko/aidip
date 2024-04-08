from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):
    title = models.TextField()
    description = models.TextField()
    quantity = models.IntegerField()
    cost = models.IntegerField()
    size = models.TextField()
    model = models.TextField()
    status = models.TextField()
    cutPath = models.TextField()
    backgroundPath = models.TextField()
    imgsArray = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
