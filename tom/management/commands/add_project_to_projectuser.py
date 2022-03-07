# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 13:10:10 2018

@author: rstreet
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from tom.models import Project, ProjectUser
from sys import exit

class Command(BaseCommand):
    help = 'Associated a Project with a particular ProjectUser'
        
    def add_arguments(self, parser):
        
        parser.add_argument('userid', nargs='+', type=str)
        parser.add_argument('projectname', nargs='+', type=str)

    def handle(self,*args, **options):
        
        qs = ProjectUser.objects.all().filter(handle=options['userid'][0])
        
        if qs.count() == 0:
            
            print('ERROR: Unknown user ID')
            
            exit()
        
        else:
            
            pu = qs[0]
            
            print('Identified user '+str(pu.id))
                    
        qs = Project.objects.all().filter(name=options['projectname'][0])
        
        if qs.count() == 0:
            
            print('ERROR: Unknown project name')
            
            exit()
        
        else:
            
            p = qs[0]
            
            print('Identified project '+str(p.id))
                
        pu.projects.add(p)
        
        pu.save()
        
        print('User now has projects:')
        print(pu.projects.all())
        