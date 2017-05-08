# -*- coding: utf-8 -*-
"""
Created on Mon May  8 09:57:35 2017

@author: rstreet
"""

from os import getcwd, path, remove, environ
from sys import path as systempath
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
import ingest, observing_strategy
from tom.models import Target
import lco_interface

def test_compose_obs_requests():
    """Function to check that observing requests are properly composed from 
    the essential parameters that will be provided by the user, factoring
    in the users's observing strategy"""
    
    params = {
            'name': 'OGLE-9999-BLG-1234',
            'ra': '12:23:34.56',
            'dec': '-20:30:40.5',
            'filter': 'SDSS-i',
            'exp_time': 30.0,
            'n_exp': 2, 
            'cadence_hrs': 0.25,
            'jitter_hrs': 0.25,
            'start_obs': datetime.strptime("2017-05-20T00:01:00","%Y-%m-%dT%H:%M:%S"),
            'stop_obs': datetime.strptime("2017-05-22T00:01:00","%Y-%m-%dT%H:%M:%S"),
            'user_id': 'tester',
    }
    obs_list = observing_strategy.compose_obs_requests(params)
    
    test_obs = lco_interface.ObsRequest()
    site_list = []
    for obs in obs_list:
        assert(type(obs) == type(test_obs))
        assert(obs.exposure_times[0] == params['exp_time'])
        assert(obs.exposure_counts[0] == params['n_exp'])
        assert(obs.cadence == params['cadence_hrs'])
        assert(obs.jitter == params['jitter_hrs'])
        assert(obs.ts_submit == params['start_obs'])
        assert(obs.ts_expire == params['stop_obs'])
        #assert(obs.user_id != None)
        #assert(obs.pswd != None)
        #assert(obs.proposal_id != None)
        if obs.site not in site_list:
            site_list.append(obs.site)
        if __name__ == '__main__':
            print obs.summary(), obs.proposal_id, obs.user_id, obs.pswd
    
    assert(len(obs_list) == 3)
    assert('lsc' in site_list)
    assert('cpt' in site_list)
    assert('coj' in site_list)

if __name__ == '__main__':
    test_compose_obs_requests()
    