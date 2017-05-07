# -*- coding: utf-8 -*-
"""
Created on Mon May  1 17:51:26 2017

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

from tom.models import Target, TargetName, Project

import observation_classes

def submit_obs_requests(obs_requests):
    """Function to compose target and observing requirements into the correct
    form and to submit the request to the LCO network
    """

    for obs in obs_requests:
        ur = obs.build_cadence_request()
        obs.submit_status = obs.submit_request(ur, script_config, log=log)

    return obs_requests
    
def compose_obs_requests(params,request):
    """Function to construct an ObsRequest instance with the users 
    parameters for the observation
    
    Returns a list of ObsRequest objects
    """

    obs_strategy = strategy_config()
    
    obs_list = []
    
    for i in range(0,len(obs_strategy['sites'],1):
        obs = observation_classes.ObsRequest()
        obs.name = params['name']
        obs.ra = params['ra']
        obs.dec = params['dec']
        obs.site = obs_strategy['sites'][i]
        obs.observatory= obs_strategy['dome'][i]
        obs.tel = obs_strategy['telescope'][i]
        obs.instrument = obs_strategy['instruments'][i]
        obs.instrument_class = '1M0-SCICAM-SINISTRO'
        obs.set_aperture_class()
        obs.filters = [ params['filter'] ]
        obs.exposure_times = [ params['exp_time'] ]
        obs.exposure_counts = [ params['n_exp'] ]
        obs.binning = 1
        obs.defocus = strategy['defocus']
        obs.cadence = params['cadence_hrs']
        obs.jitter = params['jitter_hrs']
        obs.priority = strategy['priority']
        obs.ts_submit = params['start_obs']
        obs.ts_expire = params['stop_obs']
        obs.proposal_id = strategy['proposal_id']
        obs.user_id = strategy['lco_observer_id']
        obs.pswd = strategy['lco_observer_pswd']
        obs.get_group_id()
        
        obs_list.append(obs)
        
    return obs

def strategy_config(request):
    """Function defining the pre-determined parameters of observations for 
    the current project, including which sites, telescopes, instruments etc
    and to apply any pre-set observation parameters defined by the user for
    their specific science purpose.
    """
    
    obs_strategy = {}
    strategy['sites'] = [ 'lsc', 'cpt', 'coj' ]
    strategy['domes'] = [ 'domc', 'domc', 'domb' ]
    strategy['instrments'] = [ 'fl04', 'fl16', 'fl19' ]  XXX
    strategy['defocus'] = 0.0
    strategy['priority'] = 1.0
    
    qs = Project.objects.all()
    project = qs[0]
    strategy['proposal_id'] = project.proposal_id
    
    qs = User.object.filter(user_handle__contains=request.user)
    if len(qs) == 1:
        strategy['lco_observer_id'] = qs[0].lco_observer_id
        strategy['lco_observer_pswd'] = qs[0].lco_observer_pswd
    
    return obs_strategy 
    