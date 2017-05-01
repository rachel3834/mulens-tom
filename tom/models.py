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
    telescope = models.CharField("Telescope",max_length=50)
    aperture = models.FloatField(blank=True)
    instrument = models.CharField("Instrument",max_length=50)
    filters = models.CharField("Filters",max_length=50)
    exp_times = models.FloatField("Exposure times")
    n_exp = models.IntegerField("Number of exposures")
    defocus = models.FloatField("Defocus",blank=True)
    binnings = models.IntegerField("Binning",blank=True)
    track_id = models.CharField("Tracking ID",max_length=100,blank=True)
    start_obs = models.DateTimeField("Start observing timestamp",blank=True)
    stop_obs = models.DateTimeField("Stop observing timestamp",blank=True)
    cadence = models.FloatField("Cadence",blank=True)
    jitter = models.FloatField("Jitter",blank=True)
    modes = ( ('override','Rapid reponse'), ('queue','Queue') )
    obs_model = models.CharField("Observation mode",max_length=30,
                                 choices=modes,default="queue")
    stats = ( ('submitted', 'Submitted'), 
              ('active', 'Active'),
              ('expired', 'Expired') )
    status = models.CharField("Observation status",max_length=30,
                              choices=stats,default="submitted")
    last_modified_date = models.DateTimeField(
            blank=True, null=True)
    
    def __str__(self):
        return self.name
