# -*- coding: utf-8 -*-
"""
Created on Mon May  1 17:51:26 2017

@author: rstreet
"""

import os
import sys
import socket
from . import local_conf
app_config = local_conf.get_conf('mulens_tom')
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

from . import lco_interface

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
            obs.instrument_class = set_instrument_class(obs.instrument)
            obs.set_aperture_class()
            obs.filters = params['filter']
            obs.exposure_times = params['exp_time']
            obs.exposure_counts = params['n_exp']
            b = set_binning_mode(obs.instrument_class)
            obs.binning = [ b ]*len(params['filter'])
            obs.focus_offset = [ obs_strategy['defocus'] ]*len(params['filter'])
            obs.cadence = params['cadence_hrs']
            obs.jitter = params['jitter_hrs']
            obs.airmass_limit = params['airmass_limit']
            obs.lunar_distance_limit = params['lunar_distance_limit']
            obs.priority = params['ipp']
            obs.ts_submit = params['start_obs']
            obs.ts_expire = params['stop_obs']
            obs.rapid_model = params['rapid_mode']
            obs.proposal_id = obs_strategy['proposal_id']
            obs.user_id = obs_strategy['lco_observer_id']
            obs.token = obs_strategy['token']
            obs.simulate = params['simulate']
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
        obs.instrument_class = set_instrument_class(obs.instrument)
        obs.set_aperture_class()
        obs.filters = params['filter']
        obs.exposure_times = params['exp_time']
        obs.exposure_counts = params['n_exp']
        b = set_binning_mode(obs.instrument_class)
        obs.binning = [ b ]*len(params['filter'])
        obs.focus_offset = [ obs_strategy['defocus'] ]*len(params['filter'])
        obs.cadence = params['cadence_hrs']
        obs.jitter = params['jitter_hrs']
        obs.airmass_limit = params['airmass_limit']
        obs.lunar_distance_limit = params['lunar_distance_limit']
        obs.priority = params['ipp']
        obs.ts_submit = params['start_obs']
        obs.ts_expire = params['stop_obs']
        obs.rapid_mode = params['rapid_mode']
        obs.proposal_id = obs_strategy['proposal_id']
        obs.user_id = obs_strategy['lco_observer_id']
        obs.token = obs_strategy['token']
        obs.simulate = params['simulate']
        obs.get_group_id()

        if obs.token == None or len(str(obs.token)) < 10:
            obs.submit_status = 'Error: Observer authentication token not set'

        obs_list.append(obs)

        if log!=None:
            log.info(obs.summary())

    return obs_list

def set_instrument_class(instrument):
    """Function to set the instrument class parameter, depending on the
    instrument name given"""

    icode = str(instrument).lower()

    if 'fl' in icode or 'fa' in icode:

        instrument_class = '1M0-SCICAM-SINISTRO'

    elif 'fs' in icode:

        instrument_class = '2M0-SCICAM-SPECTRAL'

    elif 'kb' in icode:

        instrument_class = '0M4-SCICAM-SBIG'

    else:

        instrument_class = '0M4-SCICAM-SBIG'

    return instrument_class

def set_binning_mode(instrument_class):
    """Function to set the default binning mode depending on the instrument
    class"""

    if instrument_class in ['1M0-SCICAM-SINISTRO', '0M4-SCICAM-SBIG']:

        binning = 1

    elif instrument_class == '2M0-SCICAM-SPECTRAL':

        binning = 2

    else:

        binning = 1

    return binning

def strategy_config(params):
    """Function defining the pre-determined parameters of observations for
    the current project, including which sites, telescopes, instruments etc
    and to apply any pre-set observation parameters defined by the user for
    their specific science purpose.
    """

    obs_strategy = {'sites':[], 'domes':[], 'telescopes':[], 'instruments':[]}

    try:

        if 'aperture_class' in params.keys():

            for f in params['project'].default_locations.all():

                if f.telescope == params['aperture_class']:

                    obs_strategy['sites'].append(f.site)
                    obs_strategy['domes'].append(f.enclosure)
                    obs_strategy['telescopes'].append(f.telescope)
                    obs_strategy['instruments'].append(f.instrument)

        else:

            for f in params['project'].default_locations.all():

                obs_strategy['sites'].append(f.site)
                obs_strategy['domes'].append(f.enclosure)
                obs_strategy['telescopes'].append(f.telescope)
                obs_strategy['instruments'].append(f.instrument)

    except TypeError:

        qs = ObservingFacility.objects.all()

        for f in qs:
            obs_strategy['sites'].append(f.site)
            obs_strategy['domes'].append(f.enclosure)
            obs_strategy['telescopes'].append(f.telescope)
            obs_strategy['instruments'].append(f.instrument)

    obs_strategy['defocus'] = 0.0

    obs_strategy['proposal_id'] = params['project'].proposal_id

    qs = ProjectUser.objects.filter(handle__contains=params['user_id'])

    if len(qs) == 1:
        obs_strategy['lco_observer_id'] = qs[0].lco_observer_id
        obs_strategy['token'] = qs[0].token

    return obs_strategy

def get_site_tel_inst_combinations(project):
    """Function to return the valid combinations of site, domes, telescopes
    and instruments for the LCO network.  While this would be best done by
    querying the network itself, this doesn't return the instrument details.
    """

    locations = []

    for f in ObservingFacility.objects.all():

        for ap in project.allowed_apertures.all():

            if f.telescope == ap.code:

                locations.append( (f.name+' ('+str(f.telescope)+')', f.code()) )

    return locations

def get_allowed_aperture_classes(project):
    """Function to return a list of tuples for the aperture classes
    which this project has access to"""

    aperture_classes = []

    for ap in project.allowed_apertures.all():

        aperture_classes.append( (ap.name, ap.code) )

    return aperture_classes
