# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import Target, TargetName, PhotObs, ProjectUser, Project
from .models import TargetList, ObservingFacility, ExposureSet
from .forms import TargetForm, TargetNameForm, AccountForm
from .forms import ExposureSetForm
from .forms import ObservationForm, RapidObservationForm
from scripts import ingest, query_functions, log_utilities
from scripts import observing_strategy, lco_interface
import socket

def test(request):
    return render(request,'tom/test_page.html',{})

@login_required(login_url='/login/')
def home(request):

    if request.user.is_authenticated():
        
        pu = ProjectUser.objects.all().filter(handle=request.user.username)[0]

        projects_list = pu.projects.all()
        
        return render(request,'tom/user_dashboard.html',{'projects':projects_list})
        
    else:
        
        return HttpResponseRedirect('login')
    
    return render(request,'tom/user_dashboard.html',{})

@login_required(login_url='/login/')
def project(request):

    if request.user.is_authenticated():

        pu = ProjectUser.objects.all().filter(handle=request.user.username)[0]

        allowed_projects = pu.projects.all()
        
        project = Project.objects.filter(id=request.GET.get('project'))[0]

        if project in allowed_projects:
            
            return render(request,'tom/project_dashboard.html',
                      {'project':project})
        
        else:
            return render(request,'tom/user_dashboard.html',
                      {'projects':allowed_projects})
        
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
def remove_target(request):
    """Function to remove a target and target name to the database"""
    
    if request.user.is_authenticated():

        project = Project.objects.filter(id=request.GET.get('project'))[0]

        targetlist = get_project_targetlist(project)
        
        targets = []

        if targetlist != None:
            
            for t in targetlist.targets.all():
                
                tname = TargetName.objects.filter(target_id=t.id)[0]
                
                targets.append(tname.name)
                
        if request.method == "POST":
            
            nform = TargetNameForm(request.POST)
            
            if nform.is_valid():
                
                npost = nform.save(commit=False)
                
                params = {'targetname': npost.name,
                          'project': project, 'targetlist': targetlist}
                
                (status,message) = ingest.remove_target(params)
                
                return render(request, 'tom/remove_target.html', \
                                    {'project': project,
                                    'targets': targets, 'nform': nform,
                                    'message': message})
            else:
                
                nform = TargetNameForm()
                
                return render(request, 'tom/remove_target.html', \
                                    {'project': project,
                                    'targets': targets, 'nform': nform,\
                                    'message':'Form entry was invalid.\nReason:\n'+\
                                    repr(nform.errors)+\
                                    '\nPlease try again.'})
                                    
        else:

            nform = TargetNameForm()

            return render(request, 'tom/remove_target.html', \
                                    {'project': project,'targets': targets,
                                    'nform': nform,
                                    'message': 'none'})

        
    else:
        return HttpResponseRedirect('login')
 
@login_required(login_url='/login/')
def observations(request):
    
    if request.user.is_authenticated():
        
        project = Project.objects.filter(id=request.GET.get('project'))[0]
        
        obs = PhotObs.objects.filter(project_id=project.id).order_by('start_obs').reverse()
        
        groups = []
        targetnames = []
        obs_summaries = []
        start_dates = []
        end_dates = []
        
        for o in obs:

            qs = TargetName.objects.filter(target_id=o.target_id)

            name = ''

            for q in qs:

                name = q.name+'/'

            targetnames.append(name[:-1])
            
            qs = o.exposures.all()
            exps = qs[0].summary()
            
            groups.append(o.group_id)
            
            obs_summaries.append(o.location()+' '+exps)
            
            start_dates.append(o.start_obs.strftime("%Y-%m-%dT%H:%M:%S"))
            
            end_dates.append(o.stop_obs.strftime("%Y-%m-%dT%H:%M:%S"))
            
        obs_list = zip(groups,targetnames,obs_summaries,start_dates,end_dates)

        return render(request,'tom/list_observations.html',
                      {'project': project,'obs_list':obs_list})
        
    else:
        
        return HttpResponseRedirect('login')

@login_required(login_url='/login/')
def request_obs(request,obs_type='multi-site'):
    """Function to specify a new observation with all associated
    information and submit it to both the LCO network and the DB"""
    
    host_name = socket.gethostname()

    project = Project.objects.filter(id=request.GET.get('project'))[0]

    if 'rachel' in str(host_name).lower():

        config = { 'log_dir': '/Users/rstreet/spitzermicrolensing/logs/2017',
              'log_root_name': 'request_log_'+str(project.name).replace(' ','_')}

    else:

        config = { 'log_dir': '/var/www/spitzermicrolensing/logs/2017',
              'log_root_name': 'request_log_'+str(project.name).replace(' ','_')}

    locations = observing_strategy.get_site_tel_inst_combinations(project)
    
    aperture_classes = observing_strategy.get_allowed_aperture_classes(project)
    
    if request.user.is_authenticated():
        
        project = Project.objects.filter(id=request.GET.get('project'))[0]

        targetlist = get_project_targetlist(project)
                
        log = log_utilities.start_day_log(config,'request_obs')
        log.info('Composing observation request for '+str(project.name))
        
        targets = []
        
        if targetlist != None:
            
            message = 'Warning: You need to add targets before attempting to observe them!'
            
            for t in targetlist.targets.all():
                
                tname = TargetName.objects.filter(target_id=t.id)[0]
                
                targets.append(tname.name)
        
        targets.reverse()
        
        exp_defaults = { 'inst_filter': 'None', 
                         'exp_time': 0,
                         'n_exp': 0 }
                     
        if request.method == "POST":
            
            tform = TargetNameForm(request.POST)
            exp_forms = extract_exposure_groups(request)
            
            if project.allowed_rapid:
                oform = RapidObservationForm(request.POST)
            else:
                oform = ObservationForm(request.POST)
            
            valid = verify_form_data(tform,oform,exp_forms,log)
             
            if valid:

                tpost = tform.save(commit=False)
                opost = oform.save(commit=False)
                
                exp_sets = []
                for f in exp_forms:
                    e = f.save(commit=False)
                    exp_sets.append(e)
                    
                (params,status) = parse_obs_params(obs_type,tpost,opost,
                                          exp_sets,
                                          request,
                                          project,log=log)
                
                if status == True:
                    obs_requests = observing_strategy.compose_obs_requests(params,log=log)
    
                    (status,message) = parse_obs_status(obs_requests)
                    
                else:
                    message = 'Error: No exposure groups specified'
                    
                if status == False:

                    message = obs_requests[0].submit_status
                    
                    tform = TargetNameForm()
                    eform1 = ExposureSetForm()
                    eform2 = ExposureSetForm(initial=exp_defaults)
                    eform2.fields['init_filter'].initial = filter_idFORNONE
                    eform3 = ExposureSetForm(initial=exp_defaults)
            
                    if project.allowed_rapid:
                        oform = RapidObservationForm()
                    else:
                        oform = ObservationForm()

                    return render(request, 'tom/request_observation.html', \
                                    {'project': project, 'targets': targets,
                                    'tform': tform, 'oform': oform,
                                    'eform1': eform1,'eform2': eform2,
                                    'eform3': eform3,
                                     'obs_type': obs_type,'locations':locations,
                                     'aperture_classes': aperture_classes,
                                     'message':[message]})
                                     
                else:
                    
                    obs_requests = lco_interface.submit_obs_requests(obs_requests,log=log)
                    
                    ingest.record_obs_requests(obs_requests)
                    
                    (status,message) = parse_obs_status(obs_requests)
                
                    log_utilities.end_day_log( log )
                
                    return render(request, 'tom/request_observation.html', \
                                    {'project': project, 'targets': targets,
                                    'tform': tform, 'oform': oform,
                                    'eform1': exp_forms[0],'eform2': exp_forms[1],
                                    'eform3': exp_forms[2],
                                    'obs_type': obs_type,'locations':locations,
                                    'aperture_classes': aperture_classes,
                                    'message': message})
                                    
            else:
                
                tform = TargetNameForm()
                eform1 = ExposureSetForm()
                eform2 = ExposureSetForm(initial=exp_defaults)
                eform3 = ExposureSetForm(initial=exp_defaults)
            
                if project.allowed_rapid:
                    oform = RapidObservationForm()
                else:
                    oform = ObservationForm()
                    
                if len(targets) == 0:
                    
                    message = 'Warning: You need to add targets before attempting to observe them!'
                    
                log_utilities.end_day_log( log )
                    
                return render(request, 'tom/request_observation.html', \
                                    {'project': project, 'targets': targets,
                                    'tform': tform, 'oform': oform,
                                    'eform1': eform1,'eform2': eform2,
                                    'eform3': eform3,
                                    'obs_type': obs_type,'locations':locations,
                                    'aperture_classes': aperture_classes,
                                    'message':['Form entry was invalid.  Please try again.']})
                                    
        else:

            tform = TargetNameForm()
            eform1 = ExposureSetForm()
            eform2 = ExposureSetForm(initial=exp_defaults)
            eform3 = ExposureSetForm(initial=exp_defaults)
            
            if project.allowed_rapid:
                oform = RapidObservationForm()
            else:
                oform = ObservationForm()

            if len(targets) == 0:
                
                message = 'Warning: You need to add targets before attempting to observe them!'
            
            log_utilities.end_day_log( log )
            
            return render(request, 'tom/request_observation.html', \
                                    {'project': project,
                                    'tform': tform, 'oform': oform, 
                                    'eform1': eform1,'eform2': eform2,
                                    'eform3': eform3,
                                     'targets': targets,'obs_type': obs_type,
                                    'locations':locations,
                                    'aperture_classes': aperture_classes,
                                    'message': []})

    else:
        
        return HttpResponseRedirect('login')

def extract_exposure_groups(request):
    """Function to extract the data for multiple exoposure groups"""
    
    data = request.POST.copy()
    
    exp_sets = []
    
    for i in range(0,3,1):
        
        pars = {'inst_filter': data.getlist('inst_filter')[i],
             'exp_time': float(data.getlist('exp_time')[i]),
             'n_exp': int(data.getlist('n_exp')[i])}
             
        e = ExposureSetForm(pars)
        
        exp_sets.append(e)
    
    return exp_sets
    
def parse_obs_params(obs_type,tpost,opost,exp_sets,
                     request,project,log=None):
    """Function to parse the posted parameters into a dictionary, 
    and resolve observation parameters where necessary
    """
    
    status = True
    
    params = {}
    params['obs_type'] = obs_type
    params['name'] = tpost.name
    target = query_functions.get_target(params['name'])
    params['ra'] = target.ra
    params['dec'] = target.dec
    params['target'] = target
    
    filters = []
    exp_times = []
    n_exps = []
    
    for e in exp_sets:
        
        f = getattr(e,'inst_filter')
        
        if 'None' not in str(e.inst_filter):
            
            filters.append(e.inst_filter)
            exp_times.append(e.exp_time)
            n_exps.append(e.n_exp)
            
    params['filter'] = filters
    params['exp_time'] = exp_times
    params['n_exp'] = n_exps
    
    if len(params['filter']) == 0:
        status = False
        
    params['group_type'] = opost.group_type
    params['cadence_hrs'] = opost.cadence
    params['jitter_hrs'] = opost.jitter
    params['start_obs'] = opost.start_obs
    params['stop_obs'] = opost.stop_obs
    params['airmass_limit'] = opost.airmass_limit
    params['ipp'] = opost.ipp
    params['rapid_mode'] = opost.rapid_mode
    params['simulate'] = opost.simulate
    
    params['user_id'] = request.user
    params['project'] = project
    
    if obs_type == 'single-site':
        params['location'] = request.POST['location']
    
    if obs_type == 'multi-site':
        params['aperture_class'] = request.POST['aperture_class']
        
    if log!=None:
        for key, value in params.items():
            log.info(str(key)+' = '+str(value))
    
    return params, status

def parse_obs_status(obs_requests):
    """Function to parse the output of the requested observations"""
    
    status = True

    message = []

    for obs in obs_requests:
        
        status = obs.get_submit_status()
        
        if status:
        
            message.append(str(obs.group_id)+':'+str(obs.submit_response))

        else:
            
            message.append(str(obs.group_id)+':'+str(obs.submit_status))

    return status, message

def verify_form_data(tform,oform,exp_sets,log):
    """Function to record the verification of the input data for an
    observation request, and to log information on faults, if any."""
    
    valid = True
    
    if tform.is_valid():
        
        log.info('Target information form validation: '+repr(tform.is_valid()))
    
    else:
        
        valid = False
        log.info('Problem with target information provided: '+repr(tform.cleaned_data))
    
    if oform.is_valid():
        
        log.info('Observation information form validation: '+repr(oform.is_valid()))
    
    else:
    
        valid = False
        log.info('Problem with observation information provided: '+repr(oform.cleaned_data))
    
    for i,e in enumerate(exp_sets):
        
        if e.is_valid():
            
            log.info('Exposure information form validation (group '+str(i)+'): '+repr(e.is_valid()))
        
        else:
            
            valid = False
            log.info('Problem with exposure information provided (group '+str(i)+')')
    
    return valid

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