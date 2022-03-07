# -*- coding: utf-8 -*-
"""
Created on Mon May  8 16:45:47 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath, argv
cwd = getcwd()
systempath.append(path.join(cwd,'..'))
from local_conf import get_conf
app_config = get_conf('mulens_tom')
systempath.append(app_config)
environ.setdefault('DJANGO_SETTINGS_MODULE', 'mulens_tom.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
setup()
import ingest
import test_lco_interface

def test_record_obs_requests():
    """Function to test the ingest of the parameters of observations
    directly from the ObsRequest object instances
    """
    
    obs = test_lco_interface.get_test_obs()
    
    obs.track_id = '000012345678'
    obs.submit_status='active'
    
    ingest.record_obs_requests( [obs] )

def test_record_user_params():
    """Function to test the ingest of new parameters for a ProjectUser"""
    
    params = { 'handle': 'tester', 
              'email': 'tester@lco.global',
              'affiliation': 'LCO',
              'lco_observer_id': 'tester@lco',
              }
    
    message = ingest.record_project_user(params)
    print message
    
if __name__ == '__main__':
    test_record_obs_requests()
    #test_record_user_params()
    