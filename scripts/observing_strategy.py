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
from tom.models import ObservingFacility

import lco_interface
    
def compose_obs_requests(params,log=None):
    """Function to construct an ObsRequest instance with the users 
    parameters for the observation
    
    Returns a list of ObsRequest objects
    """
    
    obs_strategy = strategy_config(params)
    if params['obs_type'] == 'multi-site':
        if log!=None:
            log.info('Applying multi-site observing strategy parameters:')
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
            obs.user_id = obs_strategy['lco_observer_id']
            obs.token = obs_strategy['token']
            obs.simulate = False
            obs.get_group_id()
            
            if obs.token == None or len(str(obs.token)) < 10:
                obs.submit_status = 'Error: Observer authentication token not set'
            
            obs_list.append(obs)
            
            if log!=None:
                log.info(obs.summary())
    else:
        if log!=None:
            log.info('Composing single-site observing request for '+params['location'])
        location = str(params['location']).split('.')
        obs_list = []
        obs = lco_interface.ObsRequest()
        obs.name = params['name']
        obs.ra = params['ra']
        obs.dec = params['dec']
        obs.site = location[0]
        obs.observatory= location[1]
        obs.tel = location[2]
        obs.instrument = location[3]
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
        obs.user_id = obs_strategy['lco_observer_id']
        obs.token = obs_strategy['token']
        obs.simulate = False
        obs.get_group_id()
        
        if obs.token == None or len(str(obs.token)) < 10:
            obs.submit_status = 'Error: Observer authentication token not set'
        
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
    
    obs_strategy = {'sites':[], 'domes':[], 'telescopes':[], 'instruments':[]}
    
    for f in params['project'].default_locations:
        
        obs_strategy['sites'].append(f.site)
        obs_strategy['domes'].append(f.enclosure)
        obs_strategy['telescopes'].append(f.telescope)
        obs_strategy['instruments'].append(f.instrument)
        
    obs_strategy['defocus'] = 0.0
    obs_strategy['priority'] = 1.1
    
    obs_strategy['proposal_id'] = project.proposal_id
    
    qs = ProjectUser.objects.filter(handle__contains=params['user_id'])
    
    if len(qs) == 1:
        obs_strategy['lco_observer_id'] = qs[0].lco_observer_id
        obs_strategy['token'] = qs[0].token
        
    return obs_strategy 

def get_site_tel_inst_combinations():
    """Function to return the valid combinations of site, domes, telescopes 
    and instruments for the LCO network.  While this would be best done by
    querying the network itself, this doesn't return the instrument details.
    """

    locations = []
    
    for f in ObservingFacility.objects.all():
        
        locations.append( (f.name, f.code()) )
        
    return locations
    