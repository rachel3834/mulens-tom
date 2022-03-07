# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 12:54:38 2018

@author: rstreet
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from tom.models import Project, ProjectUser
from sys import exit

class Command(BaseCommand):
    help = 'Return the Projects associated with a particular ProjectUser'
        
    def add_arguments(self, parser):
        
        parser.add_argument('handle', nargs='+', type=str)

    def handle(self,*args, **options):
        
        pu = ProjectUser.objects.all().filter(handle=options['handle'][0])[0]

        if pu.projects.count() > 0:
            
            print('User '+options['handle'][0]+\
                ' is a member of the following projects:')
            
            for p in pu.projects.all():
                
                print(p.name)
                
        else:
        
            print('User '+options['handle'][0]+\
                ' is not yet a member of any projects')
                