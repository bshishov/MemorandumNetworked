from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect, get_list_or_404, get_object_or_404
from django.template import RequestContext

import json
import os

from Nodes.models import Node, Link, Url
from helpers import *
from django.conf import settings

def get_links(user, context, identifier, provider='text'):
    context['links'] = list(Link.objects.filter(user=user, node1=identifier))
    if provider == 'file':
        context['links'] = list(Link.objects.filter(user=user, node1=identifier))
        if os.path.isdir(identifier):
            filelist = os.listdir(identifier)
            for item in filelist:
                full_path = identifier + item
                new_item = Link(user=user, node1=identifier, provider1='file', node2=full_path, provider2='file')
                if os.path.isdir(full_path):
                    new_item.relation = 'folder'
                    new_item.node2 += os.sep
                else:
                    new_item.relation = 'file'
                context['links'].append(new_item)
    return context

def get_parent_links(user, context, identifier, provider='text'):
    context['parent_links'] = []
    nodes = [l.node1 for l in Link.objects.filter(user=user, node2=identifier, provider1='text')]
    urls = [l.node1 for l in Link.objects.filter(user=user, node2=identifier, provider1='url')]
    context['parent_links'] += list(Node.objects.filter(user=user, id__in=nodes))
    context['parent_links'] += list(Url.objects.filter(user=user, url_hash__in=urls))
    if provider == 'file' and identifier != '/':
        context['parent_links'].append(os.path.abspath(os.path.join(identifier, os.pardir)))
    return context

def get_links_descriptions(context):
    int_ids = []
    url_ids = []
    for link in context['links']:
        if try_parse_int(link.node2) is not None:
            int_ids.append(link.node2)
        if link.provider2 == 'url':
            url_ids.append(link.node2)
    linked_nodes = Node.objects.filter(id__in=int_ids)
    linked_urls = Url.objects.filter(url_hash__in=url_ids)
    for link in context['links']:
        if link.provider2 == 'text':
            connected_id = try_parse_int(link.node2)
            if connected_id is None:
                continue
            for node in linked_nodes:
                if connected_id == node.id:
                    link.content = node
                    break
        elif link.provider2 == 'file':
            stat = ''
            isdir = False
            if os.path.isdir(link.node2):
                isdir = True
                title = link.node2.split(os.sep)[-2] + os.sep
            else:
                if os.path.exists(link.node2):
                    stat = os.stat(link.node2)
                title = get_filename(link.node2)
            link.content = {'stats': stat, 'isdir': isdir, 'path': link.node2, 'filename': title}
        elif link.provider2 == 'url':
            for url in linked_urls:
                if url.url_hash == link.node2:
                    link.content = url
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
def unlinked(request):
    ctx = {}
    home_id = request.user.profile.home.id
    node_links = list(Link.objects.filter(user=request.user, provider2='text').values_list('node2', flat=True))
    node_links.append(str(home_id))
    url_links = Link.objects.filter(user=request.user, provider2='url').values_list('node2', flat=True)
    ctx['nodes'] = Node.objects.filter(user=request.user).exclude(id__in=node_links)
    ctx['urls'] = Url.objects.filter(user=request.user).exclude(url_hash__in=url_links)
    return render(request, 'node.html', ctx)

@require_login(url='/login/')
def index(request):
    return text_node(request, request.user.profile.home.id)

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
    ctx['node'] = get_object_or_404(Node, user=request.user.id, id=id)
    if request.method == 'POST':
        ctx['node'].text = request.POST.get('text')
        ctx['node'].save()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    ctx = group_links(get_links(request.user, ctx, id))
    ctx = get_parent_links(request.user, ctx, id)
    return render(request, 'text_node.html', ctx)

@require_login(url='/login/')
def url_node(request, id):
    ctx = {}
    ctx['id'] = id
    ctx['provider'] = 'url'
    ctx['node'] = get_object_or_404(Url, user=request.user.id, url_hash=id)
    ctx = group_links(get_links(request.user, ctx, id))
    ctx = get_parent_links(request.user, ctx, id)
    return render(request, 'url_node.html', ctx)

@require_login(url='/login/')
def delete_node(request, id):
    url = Url.objects.get(url_hash=id)
    if url is not None:
        url.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@require_login(url='/login/')
def link(request, id):
    relation = request.POST.get('relation')
    if request.method == 'POST' and relation != '':
        link = Link.objects.get(id=id)
        link.relation = relation
        link.save()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return HttpResponseRedirect('/')

@require_login(url='/login/')
def add_node(request):
    ctx = {}
    provider = request.POST.get('new_provider')
    parent_id = request.POST.get('parent_id')
    parent_provider = request.POST.get('parent_provider')
    relation = request.POST.get('relation')
    relation_back = request.POST.get('relation_back')
    if request.method == 'POST' and relation != '':
        if provider == 'text':
            node = Node(user=request.user, text=request.POST.get('text'))
            node.save()
            make_relation(request.user, parent_id, parent_provider, node.id, provider, relation, relation_back)
        elif provider == 'url':
            url_text = request.POST.get('url')
            import hashlib
            m = hashlib.md5()
            m.update(url_text.encode('utf-8'))
            url_hash = m.hexdigest()
            try:
                title, image = get_url_info(url_text, url_hash)
                url = Url(user=request.user, url=url_text, name=title, image=image)
                url.url_hash = url_hash
                url.save()
            except:
                url = Url.objects.get(url_hash=url_hash)
            make_relation(request.user, parent_id, parent_provider, url_hash, provider, relation, relation_back)
        elif provider == 'file':
            # todo - add files
            new_path = os.path.join(parent_id, request.POST.get('name'))
            if os.path.isdir(parent_id) and os.path.isdir(new_path):
                os.mkdir(new_path)
            make_relation(request.user, parent_id, parent_provider, new_path, provider, relation, relation_back)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@require_login(url='/')
def download_file(request, id):
    if os.path.isdir(id):
        folder_name = id.split(os.sep)[-2]
        arch_name = '/tmp/%s.zip' % folder_name
        create_zip(id, arch_name)
        response = HttpResponse(content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename="%s"' % folder_name
        response['X-Sendfile'] = folder_name
        f = open(arch_name, 'rb')
        response.write(f.read())
        f.close()
        # It's usually a good idea to set the 'Content-Length' header too.
        # You can also set any other required headers: Cache-Control, etc.
        return response
    else:
        response = HttpResponse(content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename="%s"' % get_filename(id)
        response['X-Sendfile'] = get_filename(id)
        f = open(id, 'rb')
        response.write(f.read())
        f.close()
        # It's usually a good idea to set the 'Content-Length' header too.
        # You can also set any other required headers: Cache-Control, etc.
        return response

@require_login(url='/')
def open_file(request, id):
    if os.path.isdir(id):
        raise Http404
    try:
        from mimetypes import MimeTypes
        mime = MimeTypes()
        mimetype = mime.guess_type(id)
        response = HttpResponse(content_type=mimetype[0])
        f = open(id, 'rb')
        response.write(f.read())
        f.close()
        return response
    except PermissionError:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

@require_login(url='/login/')
def delete_link(request, id):
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
        ctx = group_links(get_links(request.user, ctx, id, 'file'))
        ctx = get_parent_links(request.user, ctx, id, 'file')

        from mimetypes import MimeTypes
        mime = MimeTypes()
        mimetype = mime.guess_type(id)
        managed_mimes = ['text', 'image', 'video', 'audio']
        ctx['mime'] = mimetype[0]
        base_type = None
        if ctx['mime'] is None:
            ctx['mime'] = 'text/binary'
        base_type = ctx['mime'].split('/')[0]
        
        # TODO: folder view
        if os.path.isdir(id):
            return render(request, 'file_node.html', ctx)      

        if base_type in managed_mimes:
            return render(request, 'Files/%s.html' % base_type, ctx) 

        if ctx['mime'] in settings.EDITABLE_FILE_TYPES:
            return render(request, 'Files/text.html', ctx)

        return render(request, 'file_node.html', ctx)
    else:
        raise Http404

def get_url_title(url):
    try:
        import urllib3
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(urllib3.PoolManager().urlopen('GET', url))
        title = soup.title.string
    except:
        title = url
    return title

def get_url_info(url, url_hash):
    return (get_url_title(url), '')

def make_relation(user, parent_node_id, parent_node_provider, node_id, node_provider, relation, relation_back):
    link = Link(user=user, node1=parent_node_id, provider1=parent_node_provider)
    link.node2 = node_id
    link.provider2 = node_provider
    link.relation = relation
    link.save()
    make_relation_back(user, link, relation_back)

def make_relation_back(user, link, relation_back):
    if link is not None and relation_back != '':
        new_link = Link(user=user)
        new_link.node1 = link.node2
        new_link.node2 = link.node1
        new_link.provider1 = link.provider2
        new_link.provider2 = link.provider1
        new_link.relation = relation_back
        new_link.save()

def test(request):
    return HttpResponse('ok')

def create_zip(basedir, archivename):
    from zipfile import ZipFile, ZIP_DEFLATED
    assert(os.path.isdir(basedir))
    with ZipFile(archivename, "w", ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(basedir):
            #NOTE: ignore empty directories
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[len(basedir)+len(os.sep):] #XXX: relative path
                z.write(absfn, zfn)