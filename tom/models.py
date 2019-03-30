# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class ObservingFacility(models.Model):
    class Meta:
        verbose_name_plural = "observing facilities"
        
    name = models.CharField("Name",max_length=50)
    site = models.CharField("Site",max_length=10)
    enclosure = models.CharField("Enclosure",max_length=10,blank=True,null=True)
    telescope = models.CharField("Telescope",max_length=10)
    instrument = models.CharField("Instrument",max_length=10)
    
    last_modified_date = models.DateTimeField(
            blank=True, null=True)
    
    def __str__(self):
        return self.name

    def code(self):
        return self.site+'.'+self.enclosure+'.'+self.telescope+'.'+self.instrument

class FacilityAperture(models.Model):
    name = models.CharField("Name",max_length=50)
    code = models.CharField("Code",max_length=4)
    
    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField("Name",max_length=50)
    proposal_id = models.CharField("Proposal ID",max_length=50,
                                       blank=True,null=True)
    default_locations = models.ManyToManyField(ObservingFacility,blank=True)
    allowed_apertures = models.ManyToManyField(FacilityAperture,blank=True)
    picture = models.CharField(max_length=300,blank=True)
    allowed_rapid = models.NullBooleanField(default=False,null=True)
    
    last_modified_date = models.DateTimeField(
            blank=True, null=True)
    
    def __str__(self):
        return self.name

class ProjectUser(models.Model):
    handle = models.CharField("User handle",max_length=50)
    first_name = models.CharField("First name",max_length=50)
    family_name = models.CharField("Family name",max_length=50)
    affiliation = models.CharField("Affiliation",max_length=100)
    email = models.EmailField()
    email_notifications = models.BooleanField(default=False,blank=True)
    lco_observer_id = models.CharField("LCO User ID",max_length=50,blank=True)
    lco_observer_pswd = models.CharField("LCO User login",max_length=50,blank=True)
    token = models.CharField("Token",max_length=200,
                                       blank=True,null=True)
    projects = models.ManyToManyField(Project,blank=True)
    last_modified_date = models.DateTimeField(
            blank=True, null=True)
    
    def __str__(self):
        return self.first_name+' '+self.family_name

     
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
                ('SDSS-g', 'SDSS-g'),
                ('Pan-STARRS-Z', 'Pan-STARRS-Z'),
                ('Bessell-V', 'Bessell-V'),
                ('Bessell-R', 'Bessell-R'),
                ('Cousins-Ic', 'Cousins-Ic'),
                ('None', 'None'),
                )
    inst_filter = models.CharField("Filter",max_length=15,choices=filters,default='SDSS-i')
    exp_time = models.FloatField("Exposure time")
    n_exp = models.IntegerField("Number of exposures")
    defocus = models.FloatField("Defocus",blank=True)
    binning = models.IntegerField("Binning",blank=True)
    
    def summary(self):
        return str(self.n_exp)+'x'+str(self.exp_time)+'s in '+str(self.inst_filter)

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
    airmass_limit = models.FloatField("Airmass limit",blank=True,default=1.5)
    lunar_distance_limit = models.FloatField("Lunar distance limit",blank=True,default=10.0)
    ipp = models.FloatField("IPP",blank=True,default=1.05)
    rapid_mode = models.NullBooleanField(default=False,null=True)
    obs_types = (
                ('single', 'Single'),
                ('cadence', 'Cadence'),
                )
    group_type = models.CharField("Group Type",max_length=10,choices=obs_types,default='single',blank=True)
    modes = ( ('override','Rapid reponse'), ('queue','Queue') )
    obs_mode = models.CharField("Observation mode",max_length=30,
                                 choices=modes,default="queue",blank=True)
    simulate = models.NullBooleanField(default=False,null=True)
    stats = ( ('submitted', 'Submitted'), 
              ('active', 'Active'),
              ('expired', 'Expired'),
              ('error', 'Error' ),
              ('simulated', 'Simulated'))
    status = models.CharField("Observation status",max_length=30,
                              choices=stats,default="submitted",blank=True)
    information = models.CharField("Information",max_length=300,
                              default="",null=True,blank=True)
    last_modified_date = models.DateTimeField(
            blank=True, null=True)

    def location(self):
        return str(self.site)+'.'+str(self.instrument)
            
    def __str__(self):
        return self.group_id
