from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^login', views.login),
    url(r'^logout', views.logout),

    url(r'^unlinked', views.unlinked),

    url(r'^add', views.add_node),
    url(r'^text/(?P<id>\d+)', views.text_node),
    url(r'^url/(?P<id>[0-9a-fA-F]{32})/remove', views.delete_node),
    url(r'^url/(?P<id>[0-9a-fA-F]{32})', views.url_node),

    url(r'^file/raw/(?P<id>.+)', views.open_file),
    url(r'^file/download/(?P<id>.+)', views.download_file),
    url(r'^file/(?P<id>.+)', views.file_node),

    url(r'^links/(?P<id>\d+)/remove', views.delete_link),
    url(r'^links/(?P<id>\d+)', views.link),

    url(r'^test/', views.test),
]