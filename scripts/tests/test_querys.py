# -*- coding: utf-8 -*-
"""
Created on Mon May  8 16:16:37 2017

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
import ingest, observing_strategy
from tom.models import Target, TargetName
import query_functions

def test_get_target():
    """Function to test the extraction of a target from the DB based on its 
    name"""
    
    name = 'OGLE-2017-BLG-test'
    target = query_functions.get_target(name)
    
    test_target = Target()
    assert(type(target) == type(test_target))
    
    test_name = TargetName.objects.get(target_id=target)
    assert(test_name.name == name)

def test_get_proposal():
    """Function to test the extraction of a project from the database"""

    name = "Test Project"
    id_code = 'LCO2017A-TEST'
    project = query_functions.get_proposal(name=name)
    assert(project.proposal_id == id_code)
    
    project = query_functions.get_proposal(id_code=id_code)
    assert(project.name == name)

if __name__ == '__main__':
    test_get_target()
    test_get_proposal()
    