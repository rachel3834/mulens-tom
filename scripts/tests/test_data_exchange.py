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
    
    
if __name__ == '__main__':
    test_notify_project_users()
