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

from tom.models import Target, TargetName

def add_target(params):
    """Function to add a new target to the database
    Required parameters in dictionary format:
        ra     string, sexigesimal format
        dec    string, sexigesimal format
        name   string 
    """
    messages = []
    (t,created_target) = Target.objects.get_or_create(ra=params['ra'],dec=params['dec'])
    if created_target == True:
        messages.append('Added new target location')
    (tname, created_name) = TargetName.objects.get_or_create(target_id=t, name=params['name'])
    if created_name == True:
        messages.append('Added new target name')
    
    message = ' '.join(messages)
    
    if created_target == True and created_name == True:
        return True, message
    else:
        return False, message

def record_obs_requests(obs_list):
    """Function to record a observation request in the database"""
    
    for obs in obs_list:
        
        qs = TargetName.objects.get(name=obs.name)
        target= qs[0]
    
        qs = Project.objects.get(proposal_id=obs.proposal_id)
        project = qs[0]
        
        exp_sets = []
        for i in range(0,len(obs.exposures),1):
            new_exp = ExposureSet(inst_filter=obs.filters[i],
                                      exp_time=obs.exptimes[i],
                                      n_exp = obs.n_exp[i],
                                      defocus = obs.defocus[i],
                                      binning = obs.binning[i]
                                      )
            new_exp.save()
            exp_sets.append(new_exp)
            
        new_obs = PhotObs(target_id=target,
                        project_id=project,
                        group_id=obs.group_id,
                        network='lco',
                        site=obs.site,
                        telescope=obs.telescope,
                        aperture=obs.aperture,
                        instrument=obs.instrument,
                        filters=obs.filters,
                        exposures=exp_sets,
                        track_id=obs.track_id,
                        start_obs=obs.start_obs,
                        stop_obs=obs.stop_obs,
                        cadence=obs.cadence,
                        jitter=obs.jitter,
                        mode=obs.mode,
                        status=obs.status_submit
                        )
        new_obs.save()
        
