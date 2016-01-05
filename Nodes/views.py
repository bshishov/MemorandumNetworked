from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect, get_list_or_404, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

import json
import os

from Nodes.models import Node, Link
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
            link.content = {'title': link.node2, 'details': os.stat(link.node2), 'image': 'none_image'}
        elif link.provider2 == 'url':
            link.content = {'title': link.node2, 'details': 'none_details', 'image': 'none_image'}
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

# Create your views here.

@require_login(url='/login/')
def index(request):
    ctx = {}
    ctx['node'] = get_object_or_404(Node, id=1)
    ctx = group_links(get_links(ctx, id))
    return render(request, 'text_node.html', ctx)

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
    ctx['node'] = get_object_or_404(Node, id=id)
    if request.method == 'POST':
        ctx['node'].text = request.POST.get('text')
        ctx['node'].save()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    ctx = group_links(get_links(ctx, id))
    return render(request, 'text_node.html', ctx)

@require_login(url='/login/')
def add_text_node(request):
    ctx = {}
    if request.method == 'POST':
        node = Node(text=request.POST.get('text'))
        node.save()
        return HttpResponseRedirect('/text/%i' % node.id)
    return render(request, 'add_text_node.html', ctx)

@require_login(url='/login/')
def file_node(request, id):
    ctx = {}
    if os.path.exists(id):
        ctx['path'] = id
        ctx['file'] = os.path.basename(id)
        ctx['node'] = os.stat(id)
        ctx = group_links(get_links(ctx, id, 'file'))
    return render(request, 'file_node.html', ctx)