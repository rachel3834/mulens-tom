# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 16:27:24 2019

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
import data_exchange
from tom.models import TargetName, Project, ProjectUser

def test_notify_project_users():
    
    tname = TargetName.objects.filter(id=100)[0]

    project1 = Project.objects.filter(name='Test Project')[0]
    project2 = Project.objects.filter(name='Test Project 2')[0]
    
    data_exchange.notify_project_users(project1,project2,tname)
    
def test_query_coords_rome():
    
    ra_str = '17:53:25.47'
    dec_str = '-29:46:22.7349'
    
    result = data_exchange.query_coords_rome(ra_str, dec_str)
    
    assert type(result) == type(True)
    assert result == True
    
    ra_str = '10:30:00.0'
    dec_str = '64:30:00.0'
    
    result = data_exchange.query_coords_rome(ra_str, dec_str)
    
    assert result == False
    
if __name__ == '__main__':
    
    #test_notify_project_users()
    test_query_coords_rome()