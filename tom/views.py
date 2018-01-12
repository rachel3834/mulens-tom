# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import Target, TargetName, PhotObs, ProjectUser, Project
from .models import TargetList
from .forms import TargetForm, TargetNameForm
from .forms import ObservationForm, ExposureSetForm, AccountForm
from scripts import ingest, query_functions, log_utilities
from scripts import observing_strategy, lco_interface
import socket

def test(request):
    return render(request,'tom/test_page.html',{})

@login_required(login_url='/login/')
def home(request):

    if request.user.is_authenticated():
        
        pu = ProjectUser.objects.all().filter(id=request.user.id)[0]

        return render(request,'tom/user_dashboard.html',{'projects':pu.projects.all()})
        
    else:
        
        return HttpResponseRedirect('login')
    
    return render(request,'tom/user_dashboard.html',{})

@login_required(login_url='/login/')
def project(request):

    if request.user.is_authenticated():
        
        project = Project.objects.filter(id=request.GET.get('project'))[0]

        return render(request,'tom/project_dashboard.html',
                      {'project':project})
        
    else:
        
        return HttpResponseRedirect('login')
    
    return render(request,'tom/project_dashboard.html',{})


@login_required(login_url='/login/')
def targets(request):
    
    if request.user.is_authenticated():
        
        project = Project.objects.filter(id=request.GET.get('project'))[0]

        targetlist = get_project_targetlist(project)
        
        if targetlist != None:
            
            targetnames = []
            targets = []
            
            for t in targetlist.targets.all():
    
                qs = TargetName.objects.filter(target_id=t)
    
                name = ''
    
                for q in qs:
    
                    name = q.name+'/'
    
                targetnames.append(name[:-1])
                
                targets.append(t)
    
            target_data = zip(targetnames,targets)
            
        else:
            
            target_data = []
            
        return render(request,'tom/list_targets.html',
                      {'project':project,'targets':target_data})
        
    else:
        return HttpResponseRedirect('login')

def get_project_targetlist(project):
    """Function to fetch a targetlist for a specific project"""
    
    qs = TargetList.objects.filter(project_id=project.id)
    
    if qs.count() > 0:
        
        targetlist = qs[0]
    
    else:
        
        targetlist = None
    
    return targetlist
    
@login_required(login_url='/login/')
def add_target(request):
    """Function to add a new target and target name to the database"""
    
    if request.user.is_authenticated():

        project = Project.objects.filter(id=request.GET.get('project'))[0]

        targetlist = get_project_targetlist(project)
        
        if request.method == "POST":
            
            tform = TargetForm(request.POST)
            nform = TargetNameForm(request.POST)
            
            if tform.is_valid() and nform.is_valid():
                
                tpost = tform.save(commit=False)
                npost = nform.save(commit=False)
                
                params = {'name': npost.name, 'ra': tpost.ra, 'dec': tpost.dec,
                          'project': project, 'targetlist': targetlist}
                
                (status,message) = ingest.add_target(params)
                
                return render(request, 'tom/add_target.html', \
                                    {'project': project,
                                    'tform': tform, 'nform': nform,
                                    'message': message})
            else:
                
                tform = TargetForm()
                nform = TargetNameForm()
                
                return render(request, 'tom/add_target.html', \
                                    {'project': project,
                                    'tform': tform, 'nform': nform,\
                                    'message':'Form entry was invalid.\nReason:\n'+\
                                    repr(tform.errors)+' '+repr(nform.errors)+\
                                    '\nPlease try again.'})
                                    
        else:

            tform = TargetForm()
            nform = TargetNameForm()

            return render(request, 'tom/add_target.html', \
                                    {'project': project,
                                    'tform': tform, 'nform': nform,
                                    'message': 'none'})

        
    else:
        return HttpResponseRedirect('login')
    

@login_required(login_url='/login/')
def observations(request):
    
    if request.user.is_authenticated():
        
        project = Project.objects.filter(id=request.GET.get('project'))[0]
        
        obs = PhotObs.objects.filter(project_id=project.id)
        
        targetnames = []

        for o in obs:

            qs = TargetName.objects.filter(target_id=o.target_id)

            name = ''

            for q in qs:

                name = q.name+'/'

            targetnames.append(name[:-1])

        obs_list = zip(targetnames,obs)

        return render(request,'tom/list_observations.html',
                      {'project': project,'obs_list':obs_list})
        
    else:
        
        return HttpResponseRedirect('login')

@login_required(login_url='/login/')
def request_obs(request,obs_type='multi-site'):
    """Function to specify a new observation with all associated
    information and submit it to both the LCO network and the DB"""
    
    host_name = socket.gethostname()
    
    if 'rachel' in str(host_name).lower():

        config = { 'log_dir': '/Users/rstreet/spitzermicrolensing/logs/2017',
              'log_root_name': 'request_log'}

    else:

        config = { 'log_dir': '/var/www/spitzermicrolensing/logs/2017',
              'log_root_name': 'request_log'}
    
    locations = observing_strategy.get_site_tel_inst_combinations()
    
    if request.user.is_authenticated():
        
        project = Project.objects.filter(id=request.GET.get('project'))[0]

        targetlist = get_project_targetlist(project)
                
        log = log_utilities.start_day_log(config,'request_obs')
        
        targets = []

        for t in targetlist.targets.all():
            
            tname = TargetName.objects.filter(target_id=t.id)[0]
            
            targets.append(tname.name)
        
        if request.method == "POST":
            
            tform = TargetNameForm(request.POST)
            oform = ObservationForm(request.POST)
            eform = ExposureSetForm(request.POST)
            
            if tform.is_valid() and oform.is_valid() and eform.is_valid():

                tpost = tform.save(commit=False)
                opost = oform.save(commit=False)
                epost = eform.save(commit=False)

                params = parse_obs_params(obs_type,tpost,opost,epost,request,
                                          project,log=log)
                
                obs_requests = observing_strategy.compose_obs_requests(params,log=log)

                (status,message) = parse_obs_status(obs_requests)
                
                if status == False:

                    message = obs_requests[0].submit_status
                    
                    tform = TargetNameForm()
                    oform = ObservationForm()
                    eform = ExposureSetForm()

                    return render(request, 'tom/request_observation.html', \
                                    {'project': project, 'targets': targets,
                                    'tform': tform, 'oform': oform,'eform': eform,
                                     'obs_type': obs_type,'locations':locations,
                                     'message':[message]})
                                     
                else:
                    
                    obs_requests = lco_interface.submit_obs_requests(obs_requests,log=log)
                
                    ingest.record_obs_requests(obs_requests)
                    
                    (status,message) = parse_obs_status(obs_requests)
                
                    log_utilities.end_day_log( log )
                
                    return render(request, 'tom/request_observation.html', \
                                    {'project': project, 'targets': targets,
                                    'tform': tform, 'oform': oform,'eform': eform,
                                    'obs_type': obs_type,'locations':locations,
                                    'message': message})
                                    
            else:
                
                tform = TargetNameForm()
                oform = ObservationForm()
                eform = ExposureSetForm()
                
                return render(request, 'tom/request_observation.html', \
                                    {'project': project, 'targets': targets,
                                    'tform': tform, 'oform': oform,'eform': eform,
                                    'obs_type': obs_type,'locations':locations,
                                    'message':['Form entry was invalid.  Please try again.']})
                                    
        else:

            tform = TargetNameForm()
            oform = ObservationForm()
            eform = ExposureSetForm()

            return render(request, 'tom/request_observation.html', \
                                    {'project': project,
                                    'tform': tform, 'oform': oform, 'eform': eform,
                                     'targets': targets,'obs_type': obs_type,
                                    'locations':locations,'message': []})

    else:
        
        return HttpResponseRedirect('login')
        
def parse_obs_params(obs_type,tpost,opost,epost,request,project,log=None):
    """Function to parse the posted parameters into a dictionary, 
    and resolve observation parameters where necessary
    """

    params = {}
    params['obs_type'] = obs_type
    params['name'] = tpost.name
    target = query_functions.get_target(params['name'])
    params['ra'] = target.ra
    params['dec'] = target.dec
    params['target'] = target
    
    params['filter'] = epost.inst_filter
    params['exp_time'] = epost.exp_time
    params['n_exp'] = epost.n_exp
    
    params['group_type'] = opost.group_type
    params['cadence_hrs'] = opost.cadence
    params['jitter_hrs'] = opost.jitter
    params['start_obs'] = opost.start_obs
    params['stop_obs'] = opost.stop_obs
    params['airmass_limit'] = opost.airmass_limit
    
    params['user_id'] = request.user
    params['project'] = project
    
    if obs_type == 'single-site':
        params['location'] = request.POST['location']
        
    if log!=None:
        for key, value in params.items():
            log.info(str(key)+' = '+str(value))
    
    return params
    
def parse_obs_status(obs_requests):
    """Function to parse the output of the requested observations"""
    
    status = True

    message = []

    for obs in obs_requests:

        message.append(str(obs.group_id)+':'+str(obs.submit_response))

        if 'error' in str(obs.submit_response).lower() or \
            'warning' in str(obs.submit_response).lower():
            status = False

    return status, message

@login_required(login_url='/login/')
def record_obs(request):
    """Function to add a new observation to the database with all associated
    information, including the target name"""
    
    if request.user.is_authenticated():
        
        project = Project.objects.filter(id=request.GET.get('project'))[0]

        targetlist = get_project_targetlist(project)

        targets = []

        for t in targetlist.targets.all():
            
            tname = TargetName.objects.filter(target_id=t.id)[0]
            
            targets.append(tname.name)
       
        if request.method == "POST":

            obs_type = request.POST.post('obs_type')
            tform = TargetNameForm(request.POST)
            oform = ObservationForm(request.POST)
            eform = ExposureSetForm(request.POST)

            if tform.is_valid() and oform.is_valid() and eform.is_valid():

                tpost = tform.save(commit=False)
                opost = oform.save(commit=False)
                epost = eform.save(commit=False)

                params = parse_obs_params(obs_type,tpost,opost,epost,request,project)
                                          
                (status,message) = ingest.record_observation(params)
                
                return render(request, 'tom/record_observation.html', \
                                    {'project': project, 'targets': targets,
                                    'tform': tform, 'oform': oform,'eform': eform,
                                    'message': message})

            else:
                
                tform = TargetNameForm()
                oform = ObservationForm()
                eform = ExposureSetForm()
                
                return render(request, 'tom/record_observation.html', \
                                    {'project': project, 'targets': targets,
                                    'tform': tform, 'oform': oform,'eform': eform,
                                    'message':'Form entry was invalid.\nReason:\n'+\
                                    repr(tform.errors)+' '+repr(nform.errors)+\
                                    '\nPlease try again.'})
                                    
        else:
            
            tform = TargetNameForm()
            oform = ObservationForm()
            eform = ExposureSetForm()
            
            return render(request, 'tom/record_observation.html', \
                                    {'project': project, 'targets': targets,
                                    'tform': tform, 'oform': oform, 'eform': eform,
                                    'message': 'none'})   
                                    
    else:

        return HttpResponseRedirect('login')

@login_required(login_url='/login/')
def change_password(request):
    """
    View to enable the user change their login
    """
    
    if request.user.is_authenticated():
        
        if request.method == 'POST':

            form = PasswordChangeForm(request.user, request.POST)

            if form.is_valid():
                user = form.save()

                update_session_auth_hash(request, user)
                
                message = 'User password was successfully updated!'
                
                return render(request, 'tom/change_password.html', {'form': form,
                                      'message': message})

            else:

                messages = 'Form validation error, please try again'

                form = PasswordChangeForm(request.user)

                return render(request, 'tom/change_password.html', {'form': form,
                                      'message': message})

        else:

            form = PasswordChangeForm(request.user)

            return render(request, 'tom/change_password.html', {'form': form,
                                  'message': 'none'})

    else:

        return HttpResponseRedirect('login')


@login_required(login_url='/login/')
def manage_account(request):
    """
    View to enable the user to manage aspects of their user account
    """
    
    def parse_user_params(upost):
        
        params = {}
        params['handle'] = upost.handle
        params['email'] = upost.email
        params['affiliation'] = upost.affiliation
        params['lco_observer_id'] = upost.lco_observer_id
        params['token'] = upost.token
        
        return params
        
    if request.user.is_authenticated():
        
        if request.method == 'POST':

            form = AccountForm(request.POST)

            if form.is_valid():

                upost = form.save(commit=False)
                
                params = parse_user_params(upost)
                message = ingest.record_project_user(params)
                
                return render(request, 'tom/manage_account.html', \
                                {'uform': form, 
                                'message': message})
                                
            else:

                form = AccountForm()

                return render(request, 'tom/manage_account.html', \
                                {'uform': form, 
                                'message': 'Validation error, please try again'})

        else:

            form = AccountForm()

            return render(request, 'tom/manage_account.html', \
                                {'uform': form, 
                                'message': 'none'})

    else:

        return HttpResponseRedirect('login')