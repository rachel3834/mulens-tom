# -*- coding: utf-8 -*-
"""
Created on Mon May  1 14:44:18 2017

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
import ingest
from tom.models import Target

def test_add_target():
    
    params = { 
            'name': 'OGLE-9999-BLG-1234',
            'ra': '12:23:34.56',
            'dec': '-20:30:40.5',
            }
    status,message = ingest.add_target(params)
    assert status==True

if __name__ == '__main__':
    test_add_target()
