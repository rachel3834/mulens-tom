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
    
    target = None
    
    # If the name is a concentenation of several names separated with /, 
    # first try to identify one of the separate IDs:
    if '/' in target_name:
        
        name_list = target_name.split('/')
        
    else:
        
        name_list = [ target_name ]
    
    i = 0
    while target == None and i < len(name_list):
        
        qs = TargetName.objects.filter(name=name_list[i])
    
        if len(qs) > 0:
            
            target = qs[0]
        
        i += 1
        
    # If there is still no match found, try the concatenated name:
    if target == None:
        
        qs = TargetName.objects.filter(name=name)
    
        if len(qs) > 0:
            
            target = qs[0]
    
    return target

def get_target_by_id(target_id):
    """Function to return the Target instance for a specific target, given
    its name"""
    
    target = Target.objects.filter(id=target_id)[0]
    
    return target

def get_targetname_by_id(target_id):
    """Function to return the concatenated target name, given an ID"""
    
    qs = TargetName.objects.filter(target_id=target_id)
    
    if len(qs) > 0:    
        target_name = qs[0].name
        
        for name in qs[1:]:
            target_name += '/'+name.name
        
    else:
        target_name = 'None'
    
    return target_name
    
def get_proposal(name=None,id_code=None):
    """Function to return the Project instance, given its identifier"""
    
    if name != None:
        project = Project.objects.filter(name=name)
    else:
        project = Project.objects.filter(proposal_id=id_code)
    print(project)
    
    return project
    
def get_project_user(name=None, handle=None):
    """Function to return the Project User instance, given alternative 
    identifiers"""
    
    if name != None:
        user = ProjectUser.objects.get(name=name)
    else:
        user = ProjectUser.objects.get(handle=handle)
    
    return user