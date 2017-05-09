# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class ProjectUser(models.Model):
    handle = models.CharField("User handle",max_length=50)
    first_name = models.CharField("First name",max_length=50)
    family_name = models.CharField("Family name",max_length=50)
    affiliation = models.CharField("Affiliation",max_length=100)
    email = models.EmailField()
    lco_observer_id = models.CharField("LCO User ID",max_length=50,blank=True)
    lco_observer_pswd = models.CharField("LCO User login",max_length=50,blank=True)
    last_modified_date = models.DateTimeField(
            blank=True, null=True)
    
    def __str__(self):
        return self.first_name+' '+self.family_name

class Project(models.Model):
    name = models.CharField("Name",max_length=50)
    users = models.ManyToManyField(ProjectUser,blank=True)
    proposal_id = models.CharField("Proposal ID",max_length=50,
                                       blank=True,null=True)
    token = models.CharField("Token",max_length=200,
                                       blank=True,null=True)
    last_modified_date = models.DateTimeField(
            blank=True, null=True)
    
    def __str__(self):
        return self.name

     
class Target(models.Model):
    ra = models.CharField("RA", max_length=50)
    dec = models.CharField("Dec", max_length=50)
    last_modified_date = models.DateTimeField(
            blank=True, null=True)
    
    def publish(self):
        self.last_modified_date = timezone.now()
        self.save()
        
    def __str__(self):
        return str(self.id)

class TargetName(models.Model):
    target_id = models.ForeignKey(Target)
    name = models.CharField("Name",max_length=50)
    last_modified_date = models.DateTimeField(
            blank=True, null=True)
    
    def __str__(self):
        return self.name+' '+str(self.target_id)

class TargetList(models.Model):
    name = models.CharField("Name",max_length=50)
    project_id = models.ForeignKey(Project)
    targets = models.ManyToManyField(Target,blank=True)
    last_modified_date = models.DateTimeField(
            blank=True, null=True)

    def __str__(self):
        return self.name

class ExposureSet(models.Model):
    """Class describing a set of exposures in a single filter"""
    filters = (
                ('SDSS-i', 'SDSS-i'),
                ('SDSS-r', 'SDSS-r'),
                ('Pan-STARRS-Z', 'Pan-STARRS-Z'),
                ('Bessell-V', 'Bessell-V'),
                ('Bessell-R', 'Bessell-R'),
                ('Cousins-Ic', 'Cousins-Ic'),
                )
    inst_filter = models.CharField("Filter",max_length=15,choices=filters,default='Bessell-R')
    exp_time = models.FloatField("Exposure time")
    n_exp = models.IntegerField("Number of exposures")
    defocus = models.FloatField("Defocus",blank=True)
    binning = models.IntegerField("Binning",blank=True)

    def __str__(self):
        return str(self.pk)+' '+str(self.inst_filter)+' '+str(self.exp_time)+' '+str(self.n_exp)
        
class PhotObs(models.Model):
    """Class describing the table of photometric observations
    Parameters have units:    
    exp_times       float       seconds
    cadence         float       hours
    jitter          float       hours
    """
    
    target_id = models.ForeignKey(Target)
    project_id = models.ForeignKey(Project)
    group_id = models.CharField("Group ID",max_length=50,blank=True)
    network = models.CharField("Network",max_length=50,blank=True)
    site = models.CharField("Site",max_length=50,blank=True)
    telescope = models.CharField("Telescope",max_length=50,blank=True)
    instrument = models.CharField("Instrument",max_length=50,blank=True)
    exposures = models.ManyToManyField(ExposureSet,blank=True)
    track_id = models.CharField("Tracking ID",max_length=100,blank=True)
    start_obs = models.DateTimeField("Start observing timestamp",blank=True)
    stop_obs = models.DateTimeField("Stop observing timestamp",blank=True)
    cadence = models.FloatField("Cadence",blank=True)
    jitter = models.FloatField("Jitter",blank=True)
    obs_types = (
                ('single', 'Single'),
                ('cadence', 'Cadence'),
                )
    group_type = models.CharField("Group Type",max_length=10,choices=obs_types,default='single',blank=True)
    modes = ( ('override','Rapid reponse'), ('queue','Queue') )
    obs_mode = models.CharField("Observation mode",max_length=30,
                                 choices=modes,default="queue",blank=True)
    stats = ( ('submitted', 'Submitted'), 
              ('active', 'Active'),
              ('expired', 'Expired') )
    status = models.CharField("Observation status",max_length=30,
                              choices=stats,default="submitted",blank=True)
    last_modified_date = models.DateTimeField(
            blank=True, null=True)
    
    def __str__(self):
        return self.group_id
