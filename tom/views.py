# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Target, TargetName
from .forms import AddTargetForm, AddTargetNameForm
from scripts import ingest

@login_required(login_url='/login/')
def home(request):
    return render(request,'tom/index.html',{})

@login_required(login_url='/login/')
def targets(request):
    
    if request.user.is_authenticated():
        targets = Target.objects.all()
        targetnames = []
        for t in targets:
            qs = TargetName.objects.filter(target_id=t)
            name = ''
            for q in qs:
                name = q.name+'/'
            targetnames.append(name[:-1])
        target_data = zip(targetnames,targets)
        return render(request,'tom/list_targets.html',{'targets':target_data})
        
    else:
        return HttpResponseRedirect('login')

@login_required(login_url='/login/')
def add_target(request):
    """Function to add a new target and target name to the database"""
    
    if request.user.is_authenticated():
        if request.method == "POST":
            tform = AddTargetForm(request.POST)
            nform = AddTargetNameForm(request.POST)
            if tform.is_valid() and nform.is_valid():
                tpost = tform.save(commit=False)
                npost = nform.save(commit=False)
                params = {'name': npost.name, 'ra': tpost.ra, 'dec': tpost.dec}
                (status,message) = ingest.add_target(params)
                
                return render(request, 'tom/add_target.html', \
                                    {'tform': tform, 'nform': nform,
                                    'message': message})
            else:
                tform = AddTargetForm()
                nform = AddTargetNameForm()
                return render(request, 'tom/add_target.html', \
                                    {'tform': tform, 'nform': nform,\
                                    'message':'Form entry was invalid.\nReason:\n'+\
                                    repr(tform.errors)+' '+repr(nform.errors)+\
                                    '\nPlease try again.'})
        else:
            tform = AddTargetForm()
            nform = AddTargetNameForm()
            return render(request, 'tom/add_target.html', \
                                    {'tform': tform, 'nform': nform,
                                    'message': 'none'})

        
    else:
        return HttpResponseRedirect('login')
        
    return render(request,'tom/add_target.html',{'targets':target_data})