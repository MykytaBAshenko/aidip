from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    title = models.TextField()
    sizeArray = models.TextField(default=str(["S", "M", "L", "XL", "XXL"]))
    path = models.TextField()
    cost = models.IntegerField()




class Order(models.Model):
    title = models.TextField()
    description = models.TextField()
    quantity = models.IntegerField()
    cost = models.IntegerField()
    size = models.TextField()
    model = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.TextField()
    cutPath = models.TextField()
    backgroundPath = models.TextField()
    pdfPath = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
