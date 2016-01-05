from django.contrib import admin

from Nodes.views import Node, Link, Url

# Register your models here.

admin.site.register(Node)
admin.site.register(Link)
admin.site.register(Url)