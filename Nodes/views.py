from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect, get_list_or_404, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

import json
import os

from Nodes.models import Node, Link, Url
from helpers import *

def get_links(context, identifier, provider='text'):
    context['links'] = []
    if provider == 'text':
        links = Link.objects.filter(node1=identifier)
        context['links'] = list(links)
    elif provider == 'file':
        if os.path.isdir(identifier):
            filelist = os.listdir(identifier)
            for item in filelist:
                full_path = identifier + item
                new_item = Link(node1=identifier, provider1='file', node2=full_path, provider2='file')
                if os.path.isdir(full_path):
                    new_item.relation = 'folder'
                    new_item.node2 += os.sep
                else:
                    new_item.relation = 'file'
                context['links'].append(new_item)
    elif provider == 'url':
        pass
    return context

def get_links_descriptions(context):
    all_ids = [l.node2 for l in context['links']]
    int_ids = []
    for id in all_ids:
        if try_parse_int(id) is not None:
            int_ids.append(id)
    linked_nodes = Node.objects.filter(id__in=int_ids)
    for link in context['links']:
        if link.provider2 == 'text':
            connected_id = try_parse_int(link.node2)
            if connected_id is None:
                continue
            for node in linked_nodes:
                if connected_id == node.id:
                    link.content = {'title': node.text, 'details': node.text, 'image': 'none_image'}
                    break
        elif link.provider2 == 'file':
            if os.path.exists(link.node2):
                stat = os.stat(link.node2)
            link.content = {'title': os.path.basename(link.node2), 'details': None, 'image': 'none_image'}
        elif link.provider2 == 'url':
            url = Url.objects.get(url=link.node2)
            if url is None:
                link.content = {'title': link.node2, 'details': 'missing node', 'image': 'missing node'}
            else:
                link.content = {'title': link.node2, 'details': url.name, 'image': url.image}
    return context

def group_links(context):
    context = get_links_descriptions(context)
    groups = {}
    for link in context['links']:
        groups.setdefault(link.relation, 0)
        groups[link.relation] += 1
    grouped_links = {'ungrouped': []}
    for link in context['links']:
        if groups[link.relation] == 1:
            grouped_links['ungrouped'].append(link)
        else:
            grouped_links.setdefault(link.relation, [])
            grouped_links[link.relation].append(link)
    context['links'] = grouped_links
    return context

@require_login(url='/login/')
def index(request):
    return text_node(request, 1)

@unauthenticated_only(url='/')
def login(request):
    ctx = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        from django.contrib.auth import authenticate, login
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/')
            else:
                return redirect('/login?error=inactive')
        else:
            return redirect('/login?error=incorrect')
    return render(request, 'login.html', ctx)

@require_login(url='/')
def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('/')

@require_login(url='/login/')
def text_node(request, id):
    ctx = {}
    ctx['id'] = id
    ctx['provider'] = 'text'
    ctx['node'] = get_object_or_404(Node, id=id)
    if request.method == 'POST':
        ctx['node'].text = request.POST.get('text')
        ctx['node'].save()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    ctx = group_links(get_links(ctx, id))
    return render(request, 'text_node.html', ctx)

@require_login(url='/login/')
def add_node(request):
    ctx = {}
    if request.method == 'POST':
        link = None
        provider = request.POST.get('new_provider')
        parent_node_id = request.POST.get('parent_id')
        parent_node_provider = request.POST.get('parent_provider')
        relation = request.POST.get('relation')
        relation_back = request.POST.get('relation_back')
        if provider == 'text':
            node = Node(text=request.POST.get('text'))
            node.save()
            link = Link(node1=parent_node_id, provider1=parent_node_provider)
            link.node2 = node.id
            link.provider2 = 'text'
            link.relation = relation
            link.save()
        elif provider == 'url':
            url_text = request.POST.get('url')
            try:
                url = Url.objects.get(url=url_text)
            except:
                url = Url(url=url_text, name=get_url_title(url_text), image=make_url_screenshot(url_text))
                url.save()
            link = Link(node1=parent_node_id, provider1=parent_node_provider)
            link.node2 = url_text
            link.provider2 = 'url'
            link.relation = relation
            link.save()
        elif provider == 'file':
            new_path = os.path.join(parent_id, request.POST.get('name'))
            if os.path.isdir(parent_node_id) and os.path.isdir(new_path):
                os.mkdir(new_path)
        make_relation_back(link, relation_back)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@require_login(url='/login/')
def delete_link(request, id):
    ctx = {}
    link = Link.objects.get(id=id)
    if link is not None:
        link.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@require_login(url='/login/')
def file_node(request, id):
    ctx = {}
    ctx['id'] = id
    ctx['provider'] = 'file'
    if os.path.exists(id):
        ctx['path'] = id
        ctx['file'] = os.path.basename(id)
        ctx['node'] = os.stat(id)
        ctx = group_links(get_links(ctx, id, 'file'))
    return render(request, 'file_node.html', ctx)

def get_url_title(url):
    try:
        import urllib3
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(urllib3.PoolManager().urlopen('GET', url))
        title = soup.title.string
    except:
        title = url
    return title

def make_url_screenshot(url):
    try:
        from ghost import Ghost
        ghost = Ghost()
        import settings
        import time
        path_to_screen = os.path.join(settings.MEDIA_ROOT, str(time.time()) + '.png')
        with ghost.start() as session:
            session.open(url)
            session.set_viewport_size(1600, 1600)
            session.capture((0, 0, 1600, 1600)).scaled(150, 150).save(path_to_screen)
    except:
        path_to_screen = ''
    return path_to_screen

def make_relation_back(link, relation_back):
    if link is not None and relation_back != '':
        new_link = Link()
        new_link.node1 = link.node2
        new_link.node2 = link.node1
        new_link.provider1 = link.provider2
        new_link.provider2 = link.provider1
        new_link.relation = relation_back
        new_link.save()

def test(request):
    return HttpResponse('ok')