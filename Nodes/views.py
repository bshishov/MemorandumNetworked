from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect, get_list_or_404, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

import json

from Nodes.models import Node, Link

def render(request, path, context = {}):
    return render_to_response(path, context, RequestContext(request))

def render_json(context):
    return HttpResponse(json.dumps(context), content_type = 'application/json')

def get_int_param(request, param_name):
    param_name = request.query_params.get(param_name)
    return int(param_name) if param_name else 0

def get_links(context, identifier):
	links = Link.objects.filter(node1=identifier)
	ids = links.values_list('id', flat=True)
	context['linked_nodes'] = Node.objects.filter(id__in=ids)
	context['links'] = list(links)
	return context

# Create your views here.

def text_node(request, id):
	ctx = {}
	ctx['node'] = get_object_or_404(Node, id=id)
	ctx = get_links(ctx, id)
	return render(request, 'text_node.html', ctx)

def file_node(request, id):
	ctx = {}
	import os
	if os.path.exists(id):
		ctx['path'] = id
		ctx['file'] = os.path.basename(id)
		ctx['node'] = os.stat(id)
		ctx = get_links(ctx, id)
		if os.path.isdir(id):
			filelist = os.listdir(id)
			for item in filelist:
				full_path = id + os.sep + item
				new_item = Link(node1=id, provider1='file', node2=full_path, provider2='file')
				if os.path.isdir(full_path):
					new_item.relation = 'folder'
				else:
					new_item.relation = 'file'
				ctx['links'].append(new_item)
	return render(request, 'file_node.html', ctx)