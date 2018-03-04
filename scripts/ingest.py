# -*- coding: utf-8 -*-
"""
Created on Mon May  1 14:32:24 2017

@author: rstreet
"""
import os
import sys
import socket
from local_conf import get_conf
app_config = get_conf('mulens_tom')
sys.path.append(app_config)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mulens_tom.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
setup()

from tom.models import Target, TargetName, ExposureSet, PhotObs, ProjectUser
import query_functions, utilities

def add_target(params):
    """Function to add a new target to the database
    Required parameters in dictionary format:
        ra     string, sexigesimal format
        dec    string, sexigesimal format
        name   string 
        project Object  Project model
        targetlist Object TargetList model
    """
    
    messages = []

    (t,created_target) = Target.objects.get_or_create(ra=params['ra'],dec=params['dec'])
    
    if created_target == True:

        messages.append('Added new target location')
        
        if params['targetlist'] != None:
            
            params['targetlist'].targets.add(t)
            params['targetlist'].save()
        
    else:
        
        if params['targetlist'] != None:
            
            own_target = target_in_list(targetlist,params)
            
            if own_target:
                
                messages.append('This target is already in your target list')
        
            else:
                
                messages.append('WARNING: Target already in database.  May be being observed by another project')
                
    (tname, created_name) = TargetName.objects.get_or_create(target_id=t, name=params['name'])

    if created_name == True:

        messages.append('Added new target name')
    
    message = ' '.join(messages)
    
    if created_target == True and created_name == True:

        return True, message

    else:

        return False, message

def remove_target(params):
    """Function to remove a target from the DB"""
    
    rm_target = False
    
    messages = []
    
    for t in params['targetlist'].targets.all():
        
        tname = TargetName.objects.filter(target_id=t.id)[0]
        
        if params['targetname'] == tname.name:
            params['targetlist'].targets.remove(t)
            params['targetlist'].save()
            
            rm_target = True
            
    if not rm_target:
        
        messages.append('ERROR: Cannot find target '+params['targetname']+' in project target list')
        
    else:
        
        messages.append('Removed '+params['targetname'])
        
    message = ' '.join(messages)
    
    return rm_target, message

def target_in_list(targetlist,params):
    """Function to check whether a given target is already in a targetlist"""
    
    tol = 1.0 / 3600.0
    
    target_loc = utilities.sex2decdeg(params['ra'],params['dec'])
    
    for t in params['targetlist'].targets.all():
        
        t_loc = utilities.sex2decdeg(t.ra,t.dec)
    
        gamma = utilities.separation_two_points(target_loc,t_loc)
    
        if gamma < tol:
            
            return True
            
    return False
    
def record_obs_requests(obs_list):
    """Function to record a observation request in the database"""
    
    
    for obs in obs_list:
        
        target = query_functions.get_target(obs.name)
    
        project = query_functions.get_proposal(id_code=obs.proposal_id)
        
        if obs.get_submit_status(): 
            
            trackid = obs.track_id
            
        else:
            
            trackid = '99999999'
        
        exp_sets = []
        for i in range(0,len(obs.exposure_times),1):
            new_exp = ExposureSet(inst_filter=obs.filters[i],
                                      exp_time=obs.exposure_times[i],
                                      n_exp = obs.exposure_counts[i],
                                      defocus = obs.focus_offset[i],
                                      binning = obs.binning[i]
                                      )
            new_exp.save()
            exp_sets.append(new_exp)

        new_obs = PhotObs(target_id=target,
                        project_id=project,
                        group_id=obs.group_id,
                        network='lco',
                        site=obs.site,
                        telescope=obs.tel,
                        instrument=obs.instrument,
                        track_id=trackid,
                        start_obs=obs.ts_submit,
                        stop_obs=obs.ts_expire,
                        cadence=obs.cadence,
                        jitter=obs.jitter,
                        ipp=obs.priority,
                        rapid_mode=obs.rapid_mode,
                        simulate=obs.simulate,
                        group_type=obs.group_type,
                        status=obs.submit_status,
                        information=str(obs.submit_response)
                        )
        new_obs.save()
        
        for exp in exp_sets:
            new_obs.exposures.add(exp)

def record_project_user(params):
    """Function to record updated details of a Project User's account"""
    
    user = query_functions.get_project_user(handle=params['handle'])
    
    user.affiliation = params['affiliation']
    user.email = params['email']
    user.lco_observer_id = params['lco_observer_id']
    user.token = params['token']
    user.save()
    
    return 'Updated project user parameters'
    
