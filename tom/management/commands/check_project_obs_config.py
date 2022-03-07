# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 22:20:58 2018

@author: rstreet
"""


from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from tom.models import Project, ProjectUser
from sys import exit

class Command(BaseCommand):
    help = 'Return the Projects associated with a particular ProjectUser'
        
    def add_arguments(self, parser):
        
        parser.add_argument('id', nargs='+', type=str)

    def handle(self,*args, **options):
        
        project = Project.objects.all().filter(id=int(options['id'][0]))[0]
        
        print('Observing locations configured for: '+project.name)
        
        for f in project.default_locations.all():
            print(f.site, f.enclosure, f.telescope, f.instrument)
        