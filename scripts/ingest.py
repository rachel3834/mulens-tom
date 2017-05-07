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

def record_observation(params):
    """Function to record a observation request in the database"""
    
    # Extract the target object from the targetname
    
    # Implicit parameters:
    params['network'] = 'LCO'
    
    messages = []
    (t,created_target) = PhotObs.objects.get_or_create(
                                                target_id=params['target'].id,
                                                project_id=params['project'],
                                                group_id=params['group_id'],
                                                network=params['network'],
                                                site=params['site'],
                                                telescope=params['telescope'],
                                                aperture=params['aperture'],
                                                instrument=params['instrument'],
                                                filters=params['filters'],
                                                exp_times=params['exp_times'],
                                                n_exp=params['n_exp'],
                                                defocus=params['defocus'],
                                                binnings=params['binning'],
                                                track_id=params['track_id'],
                                                start_obs=params['start_obs'],
                                                stop_obs=params['stop_obs'],
                                                cadence=params['cadence'],
                                                jitter=params['jitter'],
                                                mode=params['mode'],
                                                status=params['status']
                                                )
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
