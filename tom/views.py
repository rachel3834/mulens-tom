# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Target, TargetName, PhotObs
from .forms import TargetForm, TargetNameForm
from .forms import ObservationForm, ExposureSetForm
from scripts import ingest, query_functions

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
            tform = TargetForm(request.POST)
            nform = TargetNameForm(request.POST)
            if tform.is_valid() and nform.is_valid():
                tpost = tform.save(commit=False)
                npost = nform.save(commit=False)
                params = {'name': npost.name, 'ra': tpost.ra, 'dec': tpost.dec}
                (status,message) = ingest.add_target(params)
                
                return render(request, 'tom/add_target.html', \
                                    {'tform': tform, 'nform': nform,
                                    'message': message})
            else:
                tform = TargetForm()
                nform = TargetNameForm()
                return render(request, 'tom/add_target.html', \
                                    {'tform': tform, 'nform': nform,\
                                    'message':'Form entry was invalid.\nReason:\n'+\
                                    repr(tform.errors)+' '+repr(nform.errors)+\
                                    '\nPlease try again.'})
        else:
            tform = TargetForm()
            nform = TargetNameForm()
            return render(request, 'tom/add_target.html', \
                                    {'tform': tform, 'nform': nform,
                                    'message': 'none'})

        
    else:
        return HttpResponseRedirect('login')
        
    return render(request,'tom/add_target.html',{'targets':target_data})

@login_required(login_url='/login/')
def observations(request):
    
    if request.user.is_authenticated():
        obs = PhotObs.objects.all()
        targetnames = []
        for o in obs:
            qs = TargetName.objects.filter(target_id=obs)
            name = ''
            for q in qs:
                name = q.name+'/'
            targetnames.append(name[:-1])
        obs_list = zip(targetnames,obs)
        return render(request,'tom/list_observations.html',{'obs_list':obs_list})
        
    else:
        return HttpResponseRedirect('login')

@login_required(login_url='/login/')
def request_obs(request):
    """Function to specify a new observation with all associated
    information and submit it to both the LCO network and the DB"""
    
    if request.user.is_authenticated():
        qs = TargetName.objects.all()
        targets = []
        for q in qs:
            targets.append(q.name)
        
        if request.method == "POST":
            tform = TargetNameForm(request.POST)
            oform = ObservationForm(request.POST)
            eform = ExposureSetForm(request.POST)
            if tform.is_valid() and oform.is_valid() and eform.is_valid():
                tpost = tform.save(commit=False)
                opost = oform.save(commit=False)
                epost = eform.save(commit=False)
                params = parse_obs_params(tpost,opost,epost,request)
                
                obs_requests = observing_strategy.compose_obs_requests(params)
                
                obs_requests = lco_interface.submit_obs_requests(obs_requests)
                
                ingest.record_obs_requests(obs_requests)
                
                return render(request, 'tom/request_observation.html', \
                                    {'tform': tform, 'oform': oform,'eform': eform,
                                    'message': message})
            else:
                tform = TargetNameForm()
                oform = ObservationForm()
                eform = ExposureSetForm()
                return render(request, 'tom/request_observation.html', \
                                    {'tform': tform, 'oform': oform,'eform': eform,
                                    'message':'Form entry was invalid.\nReason:\n'+\
                                    repr(tform.errors)+' '+repr(nform.errors)+\
                                    '\nPlease try again.'})
        else:
            tform = TargetNameForm()
            oform = ObservationForm()
            eform = ExposureSetForm()
            return render(request, 'tom/request_observation.html', \
                                    {'tform': tform, 'oform': oform, 'eform': eform,
                                     'targets': targets,
                                    'message': 'none'})

        
    else:
        return HttpResponseRedirect('login')
        
def parse_obs_params(tpost,opost,epost,request):
    """Function to parse the posted parameters into a dictionary, 
    and resolve observation parameters where necessary
    """

    params = {}
    params['name'] = tpost.name
    target = query_functions.get_target(params['name'])
    params['ra'] = target.ra
    params['dec'] = target.dec
    params['target'] = target
    
    params['filter'] = epost.inst_filter
    params['exp_time'] = epost.exp_time
    params['n_exp'] = epost.n_exp
    
    params['group_type'] = opost.group_type
    params['cadence'] = opost.cadence
    params['jitter'] = opost.jitter
    params['tart_obs'] = opost.start_obs
    params['stop_obs'] = opost.stop_obs
    
    params['user_id'] = request.user
    
    return params

@login_required(login_url='/login/')
def record_obs(request):
    """Function to add a new observation to the database with all associated
    information, including the target name"""
    
    if request.user.is_authenticated():
        if request.method == "POST":
            tform = TargetNameForm(request.POST)
            oform = ObservationForm(request.POST)
            eform = ExposureSetForm(request.POST)
            if tform.is_valid() and oform.is_valid() and eform.is_valid():
                tpost = tform.save(commit=False)
                opost = oform.save(commit=False)
                epost = eform.save(commit=False)
                params = parse_obs_params(tpost,opost,epost)
                
                (status,message) = ingest.record_observation(params)
                
                return render(request, 'tom/record_observation.html', \
                                    {'tform': tform, 'oform': oform,'eform': eform,
                                    'message': message})
            else:
                tform = TargetNameForm()
                oform = ObservationForm()
                eform = ExposureSetForm()
                return render(request, 'tom/record_observation.html', \
                                    {'tform': tform, 'oform': oform,'eform': eform,
                                    'message':'Form entry was invalid.\nReason:\n'+\
                                    repr(tform.errors)+' '+repr(nform.errors)+\
                                    '\nPlease try again.'})
        else:
            tform = TargetNameForm()
            oform = ObservationForm()
            eform = ExposureSetForm()
            return render(request, 'tom/record_observation.html', \
                                    {'tform': tform, 'oform': oform, 'eform': eform,
                                     'targets': targets,
                                    'message': 'none'})        
    else:
        return HttpResponseRedirect('login')
