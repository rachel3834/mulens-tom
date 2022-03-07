# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 09:56:07 2019

@author: rstreet
"""
import os
import sys
import socket
from . import local_conf
app_config = local_conf.get_conf('mulens_tom')
sys.path.append(app_config)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mulens_tom.settings')
from django.core import management
from django.conf import settings
from django.utils import timezone
from django import setup
from datetime import datetime, timedelta
from django.core.mail import send_mail
setup()
from astropy.coordinates import SkyCoord
from astropy import units as u
import requests

from tom.models import Project, ProjectUser, Target

def query_coords_rome(ra_str, dec_str, debug=False):
    """Function to query the ROME Project's public API to check
    whether a specific set of coordinates lie within that project's footprint.

    Accepts sexigesimal coordinate strings
    """

    c = SkyCoord(ra_str+' '+dec_str, frame='icrs', unit=(u.hourangle, u.deg))

    headers = {}

    url = 'https://robonet.lco.global/db/query_event_in_survey'

    url = os.path.join(url,'ra='+str(c.ra.value)+'&dec='+str(c.dec.value))

    response = requests.get(url, headers=headers, timeout=20)

    for line in response.text.split('\n'):
        if len(line) > 0:
            result = line.replace('\n','')

    if 'TRUE' in result:
        result = True
    else:
        result = False

    return result

def notify_project_users(project1,project2,target_name):
    """Function to notify all users of a project (who have opted in to
    notifications) that the given target is of interest to more than one
    project.

    Note that iterating over the users of both projects separately is
    done to avoid the project users from both projects receiving emails
    where all user emails are giving in the 'to:' field of the email.
    """

    def compose_message(target_name,project1,project2,user_project):

        message = '''Microlensing-TOM Notification

            The target '''+target_name.name+''' is of interest to both '''+\
            project1.name+''' and '''+project2.name+'''.

            Coordination of the observing programs is respectfully encouraged.

            You are receiving this message as a member of project '''+\
            user_project.name+'''


            Please note if you wish to unsubscribe from these warnings, you can
            do so from the Manage Account option in the microlensing-tom.
            '''

        return message

    project1_users = ProjectUser.objects.filter(projects=project1,
                                                email_notifications=True)

    project2_users = ProjectUser.objects.filter(projects=project2,
                                                email_notifications=True)

    subject = 'Microlensing-TOM: Target overlap warning'

    for user in project1_users:

        message = compose_message(target_name,project1,project2,project1)

        email_project_users(subject, message, [user.email])

    for user in project2_users:

        message = compose_message(target_name,project1,project2,project2)

        email_project_users(subject, message, [user.email])

def email_project_users(subject, message, distribution_list):
    """Function to send an email notification"""

    send_mail(
    subject,
    message,
    settings.EMAIL_HOST_USER,
    distribution_list,
    fail_silently=False,
    )
