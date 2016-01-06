from django.contrib import admin

from Nodes.views import Node, Link, Url

class NodeAdmin(admin.ModelAdmin):
	list_display = ('id', 'text', 'date_added')
	list_display_links = ('id', 'date_added')

class LinkAdmin(admin.ModelAdmin):
	list_display = ('node1', 'node2', 'provider1', 'provider2', 'relation')

class UrlAdmin(admin.ModelAdmin):
	list_display = ('url_hash', 'url', 'name', 'image', 'date_added')
	list_display_links = ('url',)

admin.site.register(Node, NodeAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Url, UrlAdmin)