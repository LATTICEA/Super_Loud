# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from subscription.views import find_sub_obj
from authentication.models import profilemodel

def index(request):
    context = {}
    if request.user.is_authenticated:
        obj = profilemodel.objects.get(user=request.user)
        subobj = subobj = find_sub_obj(obj)
        if obj.verified:
            pass
        else:
            return redirect('/not-verified')
        if obj.is_suspended:
            return redirect('/account-suspended')
        context['obj'] = obj
        context['subobj'] = subobj
    context['segment'] = 'index'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

def terms(request):
    context = {}
    if request.user.is_authenticated:
        obj = profilemodel.objects.get(user=request.user)
        subobj = subobj = find_sub_obj(obj)
        if obj.verified:
            pass
        else:
            return redirect('/not-verified')
        if obj.is_suspended:
            return redirect('/account-suspended')
        context['obj'] = obj
        context['subobj'] = subobj
    context['segment'] = 'terms'

    html_template = loader.get_template( 'terms.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):
    obj = profilemodel.objects.get(user=request.user)
    subobj = subobj = find_sub_obj(obj)
    if obj.verified:
        pass
    else:
        return redirect('/not-verified')
    if obj.is_suspended:
        return redirect('/account-suspended')

    context = {'obj':obj}
    context['obj'] = obj    
    context['subobj'] = subobj
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:
        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))
