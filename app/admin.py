from django.contrib import admin
import app.models as models


class NodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'text', 'date_added')
    list_display_links = ('id', 'date_added')


class LinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'node1', 'node2', 'provider1', 'provider2', 'relation')


class UrlAdmin(admin.ModelAdmin):
    list_display = ('user', 'url_hash', 'url', 'name', 'image', 'date_added')
    list_display_links = ('url',)


admin.site.register(models.Node, NodeAdmin)
admin.site.register(models.Link, LinkAdmin)
admin.site.register(models.Url, UrlAdmin)
admin.site.register(models.Profile)
