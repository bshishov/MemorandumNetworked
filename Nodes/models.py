from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Node(models.Model):
    user = models.ForeignKey(User)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

class Url(models.Model):
    user = models.ForeignKey(User)
    url_hash = models.CharField(max_length=32, unique=True)
    url = models.CharField(max_length=1000)
    name = models.CharField(max_length=1000)
    image = models.CharField(max_length=1000, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

class Link(models.Model):
    node1 = models.CharField(max_length=1000)
    node2 = models.CharField(max_length=1000)
    provider1 = models.CharField(max_length=100)
    provider2 = models.CharField(max_length=100)
    relation = models.CharField(max_length=100)