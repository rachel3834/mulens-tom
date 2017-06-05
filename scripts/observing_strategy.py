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

from tom.models import ProjectUser, Project

import lco_interface
    
def compose_obs_requests(params,log=None):
    """Function to construct an ObsRequest instance with the users 
    parameters for the observation
    
    Returns a list of ObsRequest objects
    """

    obs_strategy = strategy_config(params)
    if log!=None:
        log.info('Applying observing strategy parameters:')
        for key, value in obs_strategy.items():
            log.info(str(key)+': '+str(value))
   
    if log!=None:
        log.info('Observation requests built:')
             
    obs_list = []
    for i in range(0,len(obs_strategy['sites']),1):
        obs = lco_interface.ObsRequest()
        obs.name = params['name']
        obs.ra = params['ra']
        obs.dec = params['dec']
        obs.site = obs_strategy['sites'][i]
        obs.observatory= obs_strategy['domes'][i]
        obs.tel = obs_strategy['telescopes'][i]
        obs.instrument = obs_strategy['instruments'][i]
        obs.instrument_class = '1M0-SCICAM-SINISTRO'
        obs.set_aperture_class()
        obs.filters = [ params['filter'] ]
        obs.exposure_times = [ params['exp_time'] ]
        obs.exposure_counts = [ params['n_exp'] ]
        obs.binning = [ 1 ]
        obs.focus_offset = [ obs_strategy['defocus'] ]
        obs.cadence = params['cadence_hrs']
        obs.jitter = params['jitter_hrs']
        obs.airmass_limit = params['airmass_limit']
        obs.priority = obs_strategy['priority']
        obs.ts_submit = params['start_obs']
        obs.ts_expire = params['stop_obs']
        obs.proposal_id = obs_strategy['proposal_id']
        obs.token = obs_strategy['token']
        obs.user_id = obs_strategy['lco_observer_id']
        obs.pswd = obs_strategy['lco_observer_pswd']
        obs.simulate = False
        obs.get_group_id()
        
        obs_list.append(obs)
        
        if log!=None:
            log.info(obs.summary())
            
    return obs_list

def strategy_config(params):
    """Function defining the pre-determined parameters of observations for 
    the current project, including which sites, telescopes, instruments etc
    and to apply any pre-set observation parameters defined by the user for
    their specific science purpose.
    """
    
    obs_strategy = {}
    obs_strategy['sites'] = [ 'lsc', 'cpt', 'coj' ]
    obs_strategy['domes'] = [ 'domb', 'domc', 'domb' ]
    obs_strategy['telescopes'] = [ '1m0', '1m0', '1m0' ]
    obs_strategy['instruments'] = [ 'fl03', 'fl06', 'fl11' ]
    obs_strategy['defocus'] = 0.0
    obs_strategy['priority'] = 1.0
    
    qs = Project.objects.all()
    project = qs[0]
    obs_strategy['proposal_id'] = project.proposal_id
    obs_strategy['token'] = project.token
    
    qs = ProjectUser.objects.filter(handle__contains=params['user_id'])
    if len(qs) == 1:
        obs_strategy['lco_observer_id'] = qs[0].lco_observer_id
        obs_strategy['lco_observer_pswd'] = qs[0].lco_observer_pswd
    
    return obs_strategy 
    