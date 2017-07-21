# -*- coding: utf-8 -*-
"""
Created on Mon May  8 10:59:08 2017

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
import pytz
setup()
import ingest, observing_strategy
from tom.models import Target
import lco_interface, observing_strategy, log_utilities, ingest

def get_test_obs(simulate=False):
    """Function to return an example of an ObsRequest with default
    parameters for testing purposes"""
    
    obs = lco_interface.ObsRequest()
    obs.name = 'OB171186'
    obs.ra = '17:58:46.95'
    obs.dec = '-27:39:03.9'
    obs.site = 'coj'
    obs.observatory= 'domb'
    obs.tel = '1m0'
    obs.instrument = 'fl11'
    obs.instrument_class = '1M0-SCICAM-SINISTRO'
    obs.set_aperture_class()
    obs.filters = [ 'SDSS-i' ]
    obs.exposure_times = [ 300.0 ]
    obs.exposure_counts = [ 2 ]
    obs.binning = [ 1 ]
    obs.focus_offset = [ 0.0 ]
    obs.cadence = 0.5
    obs.jitter = 0.5
    obs.airmass_limit = 1.5
    obs.priority = 1.05
    obs.ts_submit = datetime.strptime('2017-06-09T10:00:00',"%Y-%m-%dT%H:%M:%S")
    obs.ts_submit = obs.ts_submit.replace(tzinfo=pytz.UTC)
    obs.ts_expire = datetime.strptime('2017-06-09T18:00:00',"%Y-%m-%dT%H:%M:%S")
    obs.ts_expire = obs.ts_expire.replace(tzinfo=pytz.UTC)
    if len(argv) == 1:
        obs.proposal_id = raw_input('Please enter the proposal ID: ')
        obs.token = raw_input('Please enter the LCO API token: ')
    else:
        obs.proposal_id = argv[1]
        obs.token = argv[2]
    obs.simulate = simulate
    obs.get_group_id()

    return obs

def test_build_cadence_request(simulate=False):
    """Function to verify that an ObsRequest can be submitted to the 
    LCO network"""
    config = { 'log_root_name': 'test_lco_interface',
              'log_dir': '.' }
    log = log_utilities.start_day_log( config, 'test_lco_interface' )
    
    obs = get_test_obs(simulate=simulate)
    
    ur = obs.build_cadence_request(log=log,debug=True)
    
    assert(type(ur) == type({'foo':'bar'}))
    ur_keys = ['group_id','observation_type','operator','ipp_value', 'requests']
    for key in ur_keys:
        assert(key in ur.keys())
    assert( len(ur['requests']) > 0 )


    molecule_keys = ['exposure_time', 'exposure_count', 'defocus', 'filter', \
                    'instrument_name', 'bin_x', 'bin_y']
    window_keys = ['start', 'end']
    location_keys = ['telescope_class', 'site', 'observatory']
    target_keys = ['name', 'ra', 'dec']
    constraints_keys = ['max_airmass', 'min_lunar_distance']
    def check_keys_present(component,expect_keys):
        status = True
        for key in expect_keys:
            if key not in component.keys() or component[key] == None:
                status = False
                print component, key, component[key], status, \
                    (key not in component.keys()), (component[key] == None)
        return status
     
    for req in ur['requests']:
        assert( len(req['molecules']) > 0)
        for mole in req['molecules']:
            status = check_keys_present(mole,molecule_keys)
            assert( status == True )
            
        assert( len(req['windows']) > 0 )
        for window in req['windows']:
            status = check_keys_present(window,window_keys)
            assert( status == True )
    
        status = check_keys_present(req['location'],location_keys)
        assert( status == True )
        
        status = check_keys_present(req['target'],target_keys)
        assert( status == True )
        
        status = check_keys_present(req['constraints'],constraints_keys)
        assert( status == True )
    
    log_utilities.end_day_log(log)
    print 'Successful test of observation request build'
    
def test_obs_submission(simulate=True):
    """Function to verify that an ObsRequest can be submitted to the 
    LCO network"""
    config = { 'log_root_name': 'test_lco_interface',
              'log_dir': '.'
            }
        
    log = log_utilities.start_day_log( config, 'test_lco_interface' )
    
    obs = get_test_obs(simulate=simulate)
    obs_list = lco_interface.submit_obs_requests( [ obs ], log )
    
    log_utilities.end_day_log(log)
    print 'Successful test of observation submission'
    return [obs]
    
if __name__ == '__main__':
    #test_build_cadence_request(simulate=False)
    obs_requests = test_obs_submission(simulate=False)
    ingest.record_obs_requests(obs_requests)