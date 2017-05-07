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

from tom.models import Target, TargetName

def get_target(target_name):
    """Function to return the Target instance for a specific target, given
    its name"""
    
    qs = TargetName.object.get(name=target_name)
    return qs[0]
    