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

from tom.models import Target, TargetName

import observation_classes

def submit_obs_request(params):
    """Function to compose target and observing requirements into the correct
    form and to submit the request to the LCO network
    """

    obs = compose_obs_request(params)
    ur = obs.build_cadence_request()
    status = obs.submit_request(ur, script_config, log=log)
    
    return status
    
def compose_obs_request(params):
    """Function to construct an ObsRequest instance with the users 
    parameters for the observation"""
    
    obs = observation_classes.ObsRequest()
    obs.name = params['target_name']
    obs.ra = params['ra']
    obs.dec = params['dec']
    obs.site = params['site']
    obs.observatory= params['dome']
    obs.tel = params['telescope']
    obs.instrument = params['instruments']
    obs.instrument_class = '1M0-SCICAM-SINISTRO'
    obs.set_aperture_class()
    obs.filters = params['filters']
    obs.exposure_times = params['exp_times']
    obs.exposure_counts = params['exp_counts']
    obs.cadence = params['cadence_hrs']
    obs.jitter = params['jitter_hrs']
    obs.priority = 1.0
    obs.ts_submit = params['start_obs']
    obs.ts_expire = params['stop_obs']
    obs.proposal_id = params['proposal_id']
    obs.pswd = params['lco_access']
    obs.focus_offset = params['defocus']
    obs.get_group_id()
    
    return obs
    