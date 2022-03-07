from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from tom.models import ProjectUser
from sys import exit
from os import path

class Command(BaseCommand):
    help = 'Get mailinglist'

    def handle(self,*args, **options):

        users = ProjectUser.objects.all()
        for user in users:
            print(user.email)
