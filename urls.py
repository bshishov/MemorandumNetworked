"""Memorandum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	url(r'^$', 'Nodes.views.index'),
	url(r'^login', 'Nodes.views.login'),
	url(r'^logout', 'Nodes.views.logout'),

	url(r'^text/(?P<id>\d+)', 'Nodes.views.text_node'),
	url(r'^add', 'Nodes.views.add_node'),

	url(r'^file/(?P<id>.+)', 'Nodes.views.file_node'),

	url(r'^links/(?P<id>\d+)/remove', 'Nodes.views.delete_link'),

    url(r'^admin/', admin.site.urls),
    url(r'^test/', 'Nodes.views.test'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
