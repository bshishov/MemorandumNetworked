from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect, get_list_or_404, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

import json
import os

from Nodes.models import Node, Link

def render(request, path, context = {}):
    return render_to_response(path, context, RequestContext(request))

def render_json(context):
    return HttpResponse(json.dumps(context), content_type = 'application/json')

def get_int_param(request, param_name):
    param_name = request.query_params.get(param_name)
    return int(param_name) if param_name else 0

def try_parse_int(s, base=10, val=None):
    try:
        return int(s, base)
    except ValueError:
        return val

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

def text_node(request, id):
    ctx = {}
    ctx['node'] = get_object_or_404(Node, id=id)
    ctx = group_links(get_links(ctx, id))
    return render(request, 'text_node.html', ctx)

def file_node(request, id):
    ctx = {}
    if os.path.exists(id):
        ctx['path'] = id
        ctx['file'] = os.path.basename(id)
        ctx['node'] = os.stat(id)
        ctx = group_links(get_links(ctx, id, 'file'))
    return render(request, 'file_node.html', ctx)