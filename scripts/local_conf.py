# -*- coding: utf-8 -*-
"""
Created on Mon May  1 14:38:51 2017

@author: rstreet
"""

def get_conf(request):
    
    from sys import path
    from os import environ
    import socket
    host_name = socket.gethostname()
    if 'rachel' in str(host_name).lower():
        path.append("/Users/rstreet/software/mulens_tom/")
        site_url = 'http://127.0.0.1:8000/'
    else:
        path.append("/var/www/mulenstom/")
        site_url = 'http://spitzer-microlensing.lco.global/'

    from django.conf import settings
    environ.setdefault('DJANGO_SETTINGS_MODULE', 'mulens_tom.settings')
    project_dir = settings.BASE_DIR
    
    paths = {'mulens_tom':project_dir,
            'site_url':site_url
            }
    answer = paths[request]
    return answer

if __name__ == '__main__':
    get_conf('mulens_tom')