from django.db import models
from django.contrib.auth.models import User
from Nodes.models import Node

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    profile_is_closed = models.BooleanField(default = True)
    home = models.ForeignKey(Node)
