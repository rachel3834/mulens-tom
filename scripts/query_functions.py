# -*- coding: utf-8 -*-
"""
Created on Sat May  6 20:23:02 2017

@author: rstreet
"""
import os
import sys
import socket
from local_conf import get_conf
app_config = get_conf('mulens_tom')
sys.path.append(app_config)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mulens_tom.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
setup()

from tom.models import Target, TargetName, Project, ProjectUser

def get_target(target_name):
    """Function to return the Target instance for a specific target, given
    its name"""
    
    target_name = TargetName.objects.get(name=target_name)
    
    return target_name.target_id

def get_proposal(name=None,id_code=None):
    """Function to return the Project instance, given its identifier"""
    
    if name != None:
        project = Project.objects.get(name=name)
    else:
        project = Project.objects.get(proposal_id=id_code)
    
    
    return project
    
def get_project_user(name=None, handle=None):
    """Function to return the Project User instance, given alternative 
    identifiers"""
    
    if name != None:
        user = ProjectUser.objects.get(name=name)
    else:
        user = ProjectUser.objects.get(handle=handle)
    
    return user