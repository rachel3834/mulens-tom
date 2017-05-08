# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 10:09:42 2016

@author: rstreet
"""

class Overhead:
    """Class describing the overheads attributed to using different classes
    of instruments on the LCOGT network"""    
    
    def __init__(self, tel, camera):
        tel = str(tel).lower()
        camera = str(camera).lower()
        
        self.tel = tel
        self.instrument_name = camera
        self.front_padding = 90.0
        self.filter_change = 2.0
        self.readout = 30.0
        
        if 'fl' in self.instrument_name: 
            self.instrument_class = 'sinistro'
        elif 'kb' in self.instrument_name:
            self.instrument_class = 'sbig'
        elif 'fs' in self.instrument_name:
            self.instrument_class = 'spectral'
        else:
            self.instrument_class = 'unknown'
        self.instrument = tel.replace('a','') + '-SCICAM-' + \
                                str(self.instrument_class).upper()
        
        network_overheads = { 
                    '1m0':   {
                            'sinistro': { 'front_padding': 240.0, 
                                          'filter_change': 2.0,
                                          'readout': 38.0
                                         },
                            'sbig':     { 'front_padding': 90.0, 
                                          'filter_change': 2.0,
                                          'readout': 15.5
                                        }
                            },
                    '2m0':   {
                            'spectral': { 'front_padding': 240.0, 
                                          'filter_change': 2.0,
                                          'readout': ( (42.0/4.0) + 12.0 )                                         }
                            }
                    }
        
        overheads = network_overheads[tel][self.instrument_class]
        self.front_padding = overheads['front_padding']
        self.filter_change = overheads['filter_change']
        self.readout = overheads['readout']
    
    def summary( self ):
        output = self.instrument_class + \
                    ': front-padding=' + str(self.front_padding) + \
                    's, filter-change=' + str(self.filter_change) + \
                    's, readout=' + str(self.readout) + 's' 
        return output
    
    def calc_group_length( self, nexp, exptime ):
        
        molecule_length = self.front_padding + self.filter_change + \
                            ( nexp * ( exptime + self.readout ) )
        return molecule_length
        