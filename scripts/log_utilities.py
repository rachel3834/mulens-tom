# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 00:00:05 2016

@author: rstreet
"""

import logging
from os import path, remove
from sys import exit
from astropy.time import Time
from datetime import datetime
import glob

def start_day_log( config, log_name, version=None ):
    """Function to initialize a new log file.  The naming convention for the
    file is [log_name]_[UTC_date].log.  A new file is automatically created 
    if none for the current UTC day already exist, otherwise output is appended
    to an existing file.
    This function also configures the log file to provide timestamps for 
    all entries.  
    
    Parameters:
        config    dictionary    Script configuration including parameters
                                log_directory  Directory path
                                log_root_name  Name of the log file
        log_name  string        Name applied to the logger Object 
                                (not to be confused with the log_root_name)
        console   Boolean       Switch to capture logging data from the 
                                stdout.  Normally set to False.
    Returns:
        log       open logger object
    """

    log_file = get_log_path( config, config['log_root_name'] )

    # To capture the logging stream from the whole script, create
    # a log instance together with a console handler.  
    # Set formatting as appropriate.
    log = logging.getLogger( log_name )
    
    if len(log.handlers) == 0:
        log.setLevel( logging.INFO )
        file_handler = logging.FileHandler( log_file )
        file_handler.setLevel( logging.INFO )
        
        formatter = logging.Formatter( fmt='%(asctime)s %(message)s', \
                                    datefmt='%Y-%m-%dT%H:%M:%S' )
        file_handler.setFormatter( formatter )

        log.addHandler( file_handler )
        
    log.info( '\n------------------------------------------------------\n')
    if version != None:
        log.info('Software version: '+version+'\n')
        
    return log

def get_log_path( config, log_root_name ):
    """Function to determine the path and name of the log file, giving it
    a date-stamp in UTC.
    
    Parameters:
        config    dictionary    Script configuration including parameters
                                log_directory  Directory path
                                log_root_name  Name of the log file   
    Returns:
        log_file  string        Path/log_name string
    """
    
    ts = Time.now()    
    ts = ts.iso.split()[0]
    
    log_file = path.join( config['log_dir'], \
                    log_root_name + '_' + ts + '.log' )
    return log_file

def end_day_log( log ):
    """Function to cleanly shutdown logging functions with last timestamped
    entry.
    Parameters:
        log     logger Object
    Returns:
        None
    """
    
    log.info( 'Processing complete\n' )
    logging.shutdown()
