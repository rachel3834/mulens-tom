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

LCO_API_URL = 'https://lco.global/observe/api/'

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
        self.priority = 1.0
        self.json_request = None
        self.ts_submit = None
        self.ts_expire = None
        self.user_id = None
        self.pswd = None
        self.proposal_id = None
        self.token = None
        self.focus_offset = []
        self.pfrm = False
        self.onem = False
        self.twom = False
        self.simulate = False
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
            
        output = str(self.name) + ' ' + str(self.ra) + ' ' + str(self.dec) + \
                ' ' + str(self.site) + ' ' + str(self.observatory) + ' ' + \
                ' ' + str(self.instrument) + ' ' + f_list + ' ' + \
                exp_list + ' ' + str(self.cadence) + ' ' + self.group_id
        return output

    def build_cadence_request(self, log=None, debug=False):
                        
        proposal = { 
                    'proposal_id': self.proposal_id,
                    'user_id'    : self.user_id, 
                    }
        if debug == True and log != None:
            log.info('Building ODIN observation request')
            log.info('Proposal dictionary: ' + str( proposal ))
            
        location = {
                    'telescope_class' : str(self.tel).replace('a',''),
                    'site':             str(self.site),
                    'observatory':      str(self.observatory)
                    }
        if debug == True and log != None:
            log.info('Location dictionary: ' + str( location ))
        
        if type(self.ra) == type(1.0):
            ra_deg = self.ra
            dec_deg = self.dec
        else:
            (ra_deg, dec_deg) = utilities.sex2decdeg(self.ra, self.dec)
        target =   {
                    'name'		    : str(self.name),
                    'ra'		          : ra_deg,
                    'dec'		    : dec_deg,
                    'proper_motion_ra'  : 0, 
                    'proper_motion_dec' : 0,
                    'parallax'	   : 0, 
                    'epoch'  	   : 2000,	  
                    }
        if debug == True and log != None:
            log.info('Target dictionary: ' + str( target ))
            
        constraints = { 
        		  'max_airmass': 1.5,
                    'min_lunar_distance': 10
                    }
        if debug == True and log != None:
            log.info('Constraints dictionary: ' + str( constraints ))
            
        self.get_group_id()
        ur = {
            'group_id': self.group_id, 
            'type': 'compound_request', 
            'operator': 'many'
              }
        reqList = []
        
        if debug == True and log != None:
            log.info('Observations start datetime: '+self.ts_submit.strftime("%Y-%m-%d %H:%M:%S"))
            log.info('Observations stop datetime: '+self.ts_expire.strftime("%Y-%m-%d %H:%M:%S"))
            
        ur['cadence'] = { 'start': self.ts_submit.strftime("%Y-%m-%d %H:%M:%S"), 
                        'end': self.ts_expire.strftime("%Y-%m-%d %H:%M:%S"), 
                        'period': float(self.cadence), 
                        'jitter': float(self.jitter) }
        ur['ipp_value'] = self.priority
        ur['requests'] = []
        
        molecule_list = self.build_molecule_list(debug=debug,log=log)
        
        if len(molecule_list) > 0:
            req = { 'observation_note':'',
                    'observation_type': 'NORMAL', 
                    'target': target , 
                    'windows': [ ],
                    'fail_count': 0,
                    'location': location,
                    'molecules': molecule_list,
                    'type': 'request', 
                    'constraints': constraints
                    }
            
            ur['requests'].append(req)
            if debug == True and log != None:
                log.info('Request dictionary: ' + str(req))

            ur = self.get_cadence_requests(ur,log=log)
            
            if 'requests' in ur.keys():
                for r in ur['requests']:
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
                    
        if debug == True and log != None:
            log.info(' -> Completed build of observation request ' + self.group_id)
            log.info(' -> Submit response: '+str(self.submit_response))
        return ur
        
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
            		 # Required fields
            		 'exposure_time'   : exptime,    
            		 'exposure_count'  : nexp,	     
            		 'filter'	   : parse_filter(f),      
            		 
            		 'type' 	   : 'EXPOSE',      
            		 'ag_name'	   : '',	     
            		 'ag_mode'	   : 'Optional',
            		 'instrument_name' : self.instrument_class,
            		 'bin_x'	   : self.binning[i],
            		 'bin_y'	   : self.binning[i],
            		 'defocus'	   : defocus      
            	       }
            if debug == True and log != None:
                log.info(' -> Molecule: ' + str(molecule))
    
            molecule_list.append(molecule)
                
        return molecule_list  
                
    def get_cadence_requests(self,ur,log=None):
        
        end_point = "/observe/service/request/get_cadence_requests"
        jur = self.talk_to_lco(ur,end_point)
        
        try:
            ur = json.loads(jur)
        except ValueError:
            if log != None:
                log.info('ERROR understanding returned cadence sequence, output is: ')
                log.info(repr(jur))
        except TypeError:
            if log != None:
                log.info('ERROR understanding returned cadence sequence, output is: ')
                log.info(repr(jur))
        
        if 'error_type' in ur.keys():
            self.submit_response = 'ERROR: '+ur['error_msg']
        
        if log != None:
            if 'error_type' in ur.keys():
                log.info('ERROR building observation request: '+ur['error_msg'])
            else:
                log.info('Received observable cadence sequence from LCO API')
            
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
                
        elif str(self.simulate).lower() == 'true':
            self.submit_status = 'SIM_add_OK'
            self.submit_response = 'Simulated'
            self.req_id = '9999999999'
            self.track_id = '99999999999'
            if log != None:
                log.info(' -> IN SIMULATION MODE: ' + self.submit_status)
        
        else:
            end_point = '/observe/service/request/submit'
            response = self.talk_to_lco(ur,end_point)
            self.parse_submit_response( response, log=log )

        if log != None:
            log.info(' -> Completed obs submission, submit response:')
            log.info(str(self.submit_response))
        
        return self.submit_status
    
    def talk_to_lco(self,ur,end_point):
        """Method to communicate with various APIs of the LCO network. 
        ur should be a user request while end_point is the URL string which 
        should be concatenated to the observe portal path to complete the URL.  
        Accepted end_points are:
            "/observe/service/request/submit"  
            "/observe/service/request/get_cadence_requests"
        """
        
        jur = json.dumps(ur)
        
        params = {'username': self.user_id ,
                  'password': self.pswd, 
                  'proposal': self.proposal_id, 
                  'request_data' : jur}
        
        urlrequest = urllib.urlencode(params)
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        
        secure_connect = httplib.HTTPSConnection("lco.global") 
        secure_connect.request("POST", end_point, urlrequest, headers) 
        submit_response = secure_connect.getresponse().read()
        secure_connect.close()
        
        return submit_response

        
    def parse_submit_response( self, submit_string, log=None, debug=False ):
        
        if debug == True and log != None:
            log.info('Request response = ' + str(submit_string) )
            
        submit_string = submit_string.replace('{','').replace('}','')
        submit_string = submit_string.replace('"','').split(',')
        
        for entry in submit_string: 
            if 'Unauthorized' in entry:
                self.submit_status = 'error'
                self.submit_response = entry
            elif 'time window' in submit_string:
      		self.submit_status = 'error'
                self.submit_response = entry
            else:
                try: 
                    (key,value) = entry.split(':')
                    self.submit_response = str(key) + ' = ' + str(value)
                    self.track_id = str(value)
                    self.submit_status = 'active'
                    self.get_request_numbers(log=log)
                except ValueError:
                    try:
                        (key,value) = entry.split('=')
                        self.submit_response = str(key) + ' = ' + str(value)
                        self.track_id = str(value)
                        self.submit_status = 'active'
                        self.get_request_numbers(log=log)
                    except:
                        self.submit_response = str(submit_string)
                        self.submit_status = 'error'
                        self.track_id = '9999999999'
                        self.req_id = '9999999999'
       
        if debug == True and log != None:
            log.info('Submit status: ' + str(self.submit_status))
            log.info('Submit response: ' + str(self.submit_response))
    
    def get_request_numbers(self,log=None):
        
        self.req_id = ''
        if self.track_id != None:
            headers = {'Authorization': 'Token ' + self.token}
            url = path.join(LCO_API_URL,'user_requests',str(self.track_id)+'/')
            response = requests.get(url, headers=headers).json()
            if 'requests' in response.keys():
                for r in response['requests']:
                    self.req_id = self.req_id +':'+str(r['request_number'])
                self.req_id = self.req_id +':'
            
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
        ur = obs.build_cadence_request(log=log)
        if log!=None:
            log.info('Build observation request for '+str(obs.group_id))
            
        obs.submit_status = obs.submit_request(ur, log=log)
        if log!=None:
            log.info('Submitted observation with status '+str(obs.submit_status))

    return obs_requests
