# coding: utf-8
from django.http import HttpResponse
from django.shortcuts import redirect

import json


def get_int_param(request, param_name):
    param_name = request.query_params.get(param_name)
    return int(param_name) if param_name else 0


def try_parse_int(s, base=10, val=None):
    try:
        return int(s, base)
    except ValueError:
        return val


def render_json(context):
    return HttpResponse(json.dumps(context), content_type='application/json')


def require_post(function=None, url='/'):
    def _decorator(view_function):
        def _view(request, *args, **kwargs):
            if request.method == 'POST':
                #do some before the view is reached stuffs here.
                return view_function(request, *args, **kwargs)
            else:
                return redirect(url)

        _view.__name__ = view_function.__name__
        _view.__dict__ = view_function.__dict__
        _view.__doc__ = view_function.__doc__

        return _view

    if function:
        return _decorator(function)
    return _decorator


def require_login(function=None, url='/'):
    def _decorator(view_function):
        def _view(request, *args, **kwargs):
            if request.user.is_authenticated():
                return view_function(request, *args, **kwargs)
            else:
                return redirect(url)

        _view.__name__ = view_function.__name__
        _view.__dict__ = view_function.__dict__
        _view.__doc__ = view_function.__doc__

        return _view

    if function:
        return _decorator(function)
    return _decorator


def unauthenticated_only(function=None, url='/'):
    def _decorator(view_function):
        def _view(request, *args, **kwargs):
            if not request.user.is_authenticated():
                return view_function(request, *args, **kwargs)
            else:
                return redirect(url)

        _view.__name__ = view_function.__name__
        _view.__dict__ = view_function.__dict__
        _view.__doc__ = view_function.__doc__

        return _view

    if function:
        return _decorator(function)
    return _decorator


def get_filename(path):
    import os
    if os.path.isdir(path):
        return ''
    return path.split(os.sep)[-1]