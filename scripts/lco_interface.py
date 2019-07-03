# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 18:07:21 2017

@author: rstreet
"""
from os import environ, path
from sys import path as systempath
from sys import exit
from time import sleep
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

import urllib
import utilities
import requests
import instrument_overheads
import json
import httplib
from sys import exit
from exceptions import ValueError

class ObsRequest:
    
    def __init__(self):
        self.name = None
        self.group_id = None
        self.track_id = None
        self.req_id = None
        self.ra = None
        self.dec = None
        self.site = None
        self.observatory = None
        self.tel = None
        self.instrument = None
        self.instrument_class = None
        self.filters = None
        self.group_type = 'cadence'
        self.exposure_times = []
        self.exposure_counts = []
        self.cadence = None
        self.jitter = None
        self.airmass_limit = 1.5
        self.lunar_distance_limit = 10.0
        self.priority = 1.0
        self.json_request = None
        self.ts_submit = None
        self.ts_expire = None
        self.proposal_id = None
        self.user_id = None
        self.token = None
        self.focus_offset = []
        self.pfrm = False
        self.onem = False
        self.twom = False
        self.simulate = False
        self.rapid_mode = False
        self.submit_response = None
        self.submit_status = None

    def get_group_id(self):
        sleep(0.00001)
        dateobj = timezone.now()
        time = float(dateobj.hour) + (float(dateobj.minute)/60.0) + \
        (float(dateobj.second)/3600.0) + (float(dateobj.microsecond)/3600e6)
        time = round(time,8)
        ctime = str(time)
        date = dateobj.strftime('%Y%m%d')
        TS = date+'T'+ctime
        self.group_id = str(self.name)+'_'+TS

    def set_aperture_class(self):
        if '0m4' in self.tel:
            self.pfrm = True
        elif '1m0' in self.tel:
            self.onem = True
        elif '2m0' in self.tel:
            self.twom = True
    
    def summary(self):
        exp_list = ''
        f_list = ''
        for i in range(0,len(self.exposure_counts),1):
            exp_list = exp_list + ' ' + str(self.exposure_counts[i])
            f_list = f_list + ' ' + self.filters[i]
            
        output = str(self.name) + ' ' + str(self.proposal_id)+ \
                ' ' + str(self.ra) + ' ' + str(self.dec) + \
                ' ' + str(self.site) + ' ' + str(self.observatory) + ' ' + \
                ' ' + str(self.instrument) + ' ' + f_list + ' ' + \
                exp_list + ' ' + str(self.cadence) + ' ' + self.group_id + ' ' + \
                str(self.airmass_limit) + ' ' + str(self.lunar_distance_limit)
                
        return output

    def build_cadence_request(self, log=None, debug=False):
                        
        if debug == True and log != None:
            log.info('Building Valhalla-AEON observation request')
        
        if self.group_id == None:
            self.get_group_id()
            
        request_group = {'name': self.group_id,
                         'proposal': self.proposal_id,
                         'ipp_value': float(self.priority),
                         'operator': 'SINGLE'}
                         
        if self.rapid_mode:
            request_group["observation_type"] = "TARGET_OF_OPPORTUNITY"
        else:
            request_group["observation_type"] = 'NORMAL'
            
        if type(self.ra) == type(1.0):
            ra_deg = self.ra
            dec_deg = self.dec
        else:
            (ra_deg, dec_deg) = utilities.sex2decdeg(self.ra, self.dec)
            
        target =   {
                    'name': str(self.name),
                    'type': 'ICRS',
                    'ra': ra_deg,
                    'dec': dec_deg,
                    'proper_motion_ra': 0, 
                    'proper_motion_dec': 0,
                    'parallax': 0, 
                    'epoch': 2000,	  
                    }
                
        if debug == True and log != None:
            log.info('Target dictionary: ' + str( target ))
       
        location = {
                    'telescope_class' : str(self.tel).replace('a',''),
                    'site':             str(self.site),
                    'observatory':      str(self.observatory)
                    }
                    
        if debug == True and log != None:
            log.info('Location dictionary: ' + str( location ))
                    
        constraints = { 
        		  'max_airmass': float(self.airmass_limit),
                    'min_lunar_distance': float(self.lunar_distance_limit)
                    }
                    
        if debug == True and log != None:
            log.info('Constraints dictionary: ' + str( constraints ))
            
        if debug == True and log != None:
            log.info('Observations start datetime: '+self.ts_submit.strftime("%Y-%m-%dT%H:%M:%S"))
            log.info('Observations stop datetime: '+self.ts_expire.strftime("%Y-%m-%dT%H:%M:%S"))
            log.info('Period [hrs]: '+str(self.cadence))
            log.info('Jitter [hrs]: '+str(self.jitter))
            
        cadence = {'start': self.ts_submit.strftime("%Y-%m-%dT%H:%M:%S"), 
                   'end': self.ts_expire.strftime("%Y-%m-%dT%H:%M:%S"), 
                    'period': float(self.cadence), 
                    'jitter': float(self.jitter) }
        
        inst_config_list = self.build_image_config_list(target, constraints)
        
        request_group['requests'] = [{'configurations': inst_config_list,
                                       'cadence': cadence,
                                       'location': location}]
        
        ur = self.get_cadence_requests(request_group,log=log)
        
        if 'requests' in ur.keys():
            for r in ur['requests']:
                if debug == True and log != None:
                        log.info(repr(r))
                if type(r) == type(u'foo'):
                    message = 'WARNING: '+repr(r)
                    if debug == True and log != None:
                        log.info(message)
                    if self.submit_response != None:
                        self.submit_response = self.submit_response+' '+message
                    else:
                        self.submit_response = message
                    self.req_id = '9999999999'
                    self.track_id = '99999999999'
                else:
                    if 'windows' in r.keys():
                        if len(r['windows']) == 0:
                            if debug == True and log != None:
                                log.info('WARNING: scheduler returned no observing windows for this target')
                            self.submit_status = 'No_obs_submitted'
                            message = 'WARNING: scheduler returned no observing windows for this target'
                            if self.submit_response != None:
                                self.submit_response = self.submit_response+' '+message
                            else:
                                self.submit_response = message
                            self.req_id = '9999999999'
                            self.track_id = '99999999999'
                        else:
                            log.info('Request windows: '+repr(r['windows']))
                    else:
                        message = 'WARNING: no observing windows returned for this request'
                        self.submit_status = 'No_obs_submitted'
                        if self.submit_response != None:
                            self.submit_response = self.submit_response+' '+message
                        else:
                            self.submit_response = message
                        self.req_id = '9999999999'
                        self.track_id = '99999999999'
        else:
            if 'detail' in ur.keys():
                self.submit_status = 'No_obs_submitted'
                if self.submit_response != None:
                    self.submit_response = self.submit_response+' '+ur['detail']
                else:
                    self.submit_response = 'WARNING: ' + ur['detail']
                if debug == True and log != None:
                        log.info('WARNING: problem obtaining observing windows for this target: '+ur['detail'])
                
        if debug == True and log != None:
            log.info(' -> Completed build of observation request ' + self.group_id)
            log.info(' -> Submit response: '+str(self.submit_response))
            
        return ur

    def build_image_config_list(self, target, constraints):
        """Function to compose the instrument configuration dictionary"""
        
        def parse_filter(f):
            filters = { 'SDSS-g': 'gp', 'SDSS-r': 'rp', 'SDSS-i': 'ip',
                       'Bessell-B': 'B', 'Bessell-V': 'V', 'Bessell-R': 'R', 'Cousins-Ic': 'I',
                       'Pan-STARRS-Z': 'zs'
                       }
            if f in filters.keys():
                return filters[f]
            else:
                raise ValueError('Unrecognized filter ('+f+') requested')
                
        config_list = []
        
        for i in range(0,len(self.exposure_times),1):
            
            config = {'type': 'EXPOSE',
                      'instrument_type': self.instrument_class,
                      'target': target,
                      'constraints': constraints,
                      'acquisition_config': {},
                      'guiding_config': {},
                      'instrument_configs': [ {
                                            'exposure_time': float(self.exposure_times[i]),
                                            'exposure_count': int(self.exposure_counts[i]),
                                            'optical_elements': {
                                                'filter': parse_filter(self.filters[i])},
                                                } ]
                      }
            
            config_list.append(config)
            
        return config_list
    
    
    def build_molecule_list(self,debug=False,log=None):
        def parse_filter(f):
            filters = { 'SDSS-g': 'gp', 'SDSS-r': 'rp', 'SDSS-i': 'ip',
                       'Bessell-B': 'B', 'Bessell-V': 'V', 'Bessell-R': 'R', 'Cousins-Ic': 'I',
                       'Pan-STARRS-Z': 'zs'
                       }
            if f in filters.keys():
                return filters[f]
            else:
                raise ValueError('Unrecognized filter ('+f+') requested')
        
        overheads = instrument_overheads.Overhead(self.tel, self.instrument)
        if debug == True and log != None:
            log.info('Instrument overheads ' + overheads.summary() )        
        
        molecule_list = []
        
        for i,exptime in enumerate(self.exposure_times):
            nexp = self.exposure_counts[i]
            f = self.filters[i]
            defocus = self.focus_offset[i]
            
            molecule = {
                        'type': 'EXPOSE',
                        'instrument_name': self.instrument_class,
                        'filter': parse_filter(f),
                        'exposure_time': exptime,
                        'exposure_count': nexp,
                        'bin_x': self.binning[i],
                        'bin_y': self.binning[i],
                        'fill_window': False,
                        'defocus': defocus,
                        'ag_mode': 'OPTIONAL',
                        }
                        
            if debug == True and log != None:
                log.info(' -> Molecule: ' + str(molecule))
    
            molecule_list.append(molecule)
                
        return molecule_list  
                
    def get_cadence_requests(self,ur,log=None):
        
        #end_point = "userrequests/cadence"
        end_point = "requestgroups/cadence"
        ur = self.talk_to_lco(ur,end_point,'POST')
        
        if 'error_type' in ur.keys():
            self.submit_response = 'ERROR: '+ur['error_msg']
        
        if log != None:
            if 'error_type' in ur.keys():
                log.info('ERROR building observation request: '+ur['error_msg'])
            else:
                log.info('Received response from LCO cadence API for request '+self.group_id)
            
        return ur
       
    def submit_request(self, ur, log=None):
        
        if self.submit_status != None or self.submit_response != None:
            self.submit_response = self.submit_response+': No_obs_submitted'
            self.req_id = '9999999999'
            self.track_id = '99999999999'
            self.submit_status = 'error'
            if log != None:
                log.info('Submission WARNING: ' + str(self.submit_status))
                log.info('Submission WARNING: ' + str(self.submit_response))
                
        elif self.simulate:
            self.submit_status = 'simulated'
            self.submit_response = 'Simulated'
            self.req_id = '9999999999'
            self.track_id = '99999999999'
            if log != None:
                log.info(' -> IN SIMULATION MODE: ' + self.submit_status)
        
        else:
            #end_point = 'userrequests'
            end_point = 'requestgroups'
            response = self.talk_to_lco(ur,end_point,'POST')
            self.parse_submit_response( response, log=log )

        if log != None:
            log.info(' -> Completed obs submission, submit response:')
            log.info(str(self.submit_response))
        
        return self.submit_status
    
    def talk_to_lco(self,ur,end_point,method):
        """Method to communicate with various APIs of the LCO network. 
        ur should be a user request while end_point is the URL string which 
        should be concatenated to the observe portal path to complete the URL.  
        Accepted end_points are:
            "userrequests" 
            "userrequests/cadence"  
        Accepted methods are:
            POST GET
        """
        
        jur = json.dumps(ur)
        
        headers = {'Authorization': 'Token ' + self.token}
        
        if end_point[0:1] == '/':
            end_point = end_point[1:]
        if end_point[-1:] != '/':
            end_point = end_point+'/'
        url = path.join('https://observe.lco.global/api',end_point)
        
        if method == 'POST':
            response = requests.post(url, headers=headers, json=ur).json()
        elif method == 'GET':
            response = requests.get(url, headers=headers, json=ur).json()
        
        return response

        
    def parse_submit_response( self, response, log=None, debug=False ):
        
        if debug == True and log != None:
            log.info('Request response = ' + str(submit_string) )
        
        if 'id' in response.keys():
            self.track_id = response['id']
            self.submit_response = 'id = '+str(response['id'])
            self.submit_status = 'active'
        else:
            self.submit_response = 'error'
            self.submit_status = 'error'
            self.track_id = '9999999999'
            self.req_id = '9999999999'
       
        if debug == True and log != None:
            log.info('Submit status: ' + str(self.submit_status))
            log.info('Submit response: ' + str(self.submit_response))
            
    def obs_record( self ):
        """Method to output a record, in standard format, of the current 
        observation request"""
        
        if 'OK' in str(self.submit_status):
            report = str(self.submit_status)
        else:
            report = str(self.submit_status) + ': ' + str(self.submit_response)
        
        output = ''
        for i, exptime in enumerate(self.exposure_times):
            output = output + \
                str(self.group_id) + ' ' + str(self.track_id) + ' ' + \
                str(self.req_id) + ' ' + \
                str(self.site) + ' ' + str(self.observatory) + ' ' + \
                str(self.tel).replace('a','') + ' ' + \
                str(self.instrument) + ' ' + str(self.name) + ' ' + \
                str(self.request_type)+ ' ' + \
                str(self.ra) + ' ' + str(self.dec) + \
                ' ' + str(self.filters[i]) + ' ' + str(exptime) + ' ' + \
                str(self.exposure_counts[i]) + ' ' + str(self.cadence) + ' ' + \
                str(self.priority) + ' ' + self.ts_submit.strftime("%Y-%m-%dT%H:%M:%S") + ' ' + \
                self.ts_expire.strftime("%Y-%m-%dT%H:%M:%S") + ' ' + \
                str(self.ttl) + ' ' + \
                str(self.focus_offset[i]) + ' ' + str(self.req_origin) + ' '\
                + str(report)+ '\n'
        return output

    def validate(self,log=None):
        """Method to verify that all parameters in a list of requests are valid
        Returns a boolean and a string message
        """

        status = True
        message = 'OK'
        
        if log!=None:
            log.info('Validating obs group: '+str(self.group_id))
        
        if self.submit_response != None:
            status = False
            message = self.submit_response
            if log!=None:
                log.info(' -> Invalid: '+message)
            return status, message
        
        if log!=None:
            log.info('Validated obs group: '+str(self.group_id)+' with status '+message)
        return status, message
    
    def get_submit_status(self):
        """Method to return a boolean indicating whether the observation
        submission was successful or not"""
        
        if 'error' in str(self.submit_response).lower() or \
            'warning' in str(self.submit_response).lower() or \
            'error' in str(self.submit_status).lower() or \
            'warning' in str(self.submit_status).lower() or \
            'invalid' in str(self.submit_status).lower():
                
            return False
        
        else:
            
            return True
            
def validate_request(ur,log=None):
    """Function to validate the parameters of a userrequest.
    Returns a boolean and a string message
    """

    status = True
    message = 'OK'
    
    if log!=None:
        log.info('Validating user request')
    
    if 'requests' not in ur.keys():
        status= False
        message= 'Error: no subrequests: '+repr(ur)
        if log!=None:
            log.info(' -> Invalid: '+message)
        return status, message
    
    for r in ur['requests']:

        if type(r) == type(u'foo'):
            status = False
            message = repr(r)
            if log!=None:
                log.info(' -> Invalid: '+message)
            return status, message
        else:
            if 'windows' not in r.keys():
                status= False
                message= 'Error: no valid observing windows in request'
                if log!=None:
                    log.info(' -> Invalid: '+message)
                return status, message
            else:
                if len(r['windows']) == 0:
                    status= False
                    message= 'Error: no valid observing windows in request'
                    if log!=None:
                        log.info(' -> Invalid: '+message)
                    return status, message
    if log!=None:
        log.info('Validated user request: '+str(ur['name'])+' with status '+message)
        
    return status, message
    
def submit_obs_requests(obs_requests, log=None):
    """Function to compose target and observing requirements into the correct
    form and to submit the request to the LCO network
    Parameters:
        obs_requests        list        List of ObsRequest objects
        log                 log object  [Optional] Open logging object
    returns
        obs_requests        list        List with submit_status paramater updated
    """

    for obs in obs_requests:
        (status,message) = obs.validate(log=log)
        
        if status == True:
            ur = obs.build_cadence_request(log=log,debug=True)
                
            (status, message) = validate_request(ur,log=log)
            
            if status:

                obs.submit_status = obs.submit_request(ur, log=log)
                
                if log!=None:
                    log.info('Submitted observation with status '+str(obs.submit_status))
                    if 'error' in str(obs.submit_status).lower():
                        log.info(ur)
            
            else:
                if log!=None:
                    log.info('Invalid userrequest: '+message)
                    if obs.submit_status != None:
                        obs.submit_status = obs.submit_status + ' ' + message
                    else:
                        obs.submit_status = message
    
    return obs_requests
