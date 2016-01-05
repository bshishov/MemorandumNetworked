from django.db import models

# Create your models here.

class Node(models.Model):
	text = models.TextField()

class Link(models.Model):
	node1 = models.CharField(max_length=1000)
	node2 = models.CharField(max_length=1000)
	provider1 = models.CharField(max_length=100)
	provider2 = models.CharField(max_length=100)
	relation = models.CharField(max_length=100)

class Url(models.Model):
	url = models.CharField(max_length=1000)
	name = models.CharField(max_length=1000)
	image = models.CharField(max_length=1000, blank=True, null=True)