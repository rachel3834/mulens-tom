# -*- coding: utf-8 -*-
"""
Created on Mon May  1 14:23:30 2017

@author: rstreet
"""

from tom.models import *
from django import forms

class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ('ra','dec')

class TargetNameForm(forms.ModelForm):
    class Meta:
        model = TargetName
        fields = ('name',)

class ObservationForm(forms.ModelForm):
    class Meta:
        model = PhotObs
        fields = ('cadence','jitter','start_obs','stop_obs','airmass_limit',
                  'lunar_distance_limit','ipp','simulate')
    start_obs = forms.DateTimeField(label='start_obs',input_formats=["%Y-%m-%dT%H:%M:%S"])
    stop_obs = forms.DateTimeField(label='stop_obs',input_formats=["%Y-%m-%dT%H:%M:%S"])
    airmass_limit = forms.FloatField(label='airmass_limit',min_value=1.0,max_value=2.2)
    lunar_distance_limit = forms.FloatField(label='lunar_distance_limit',min_value=1.0,max_value=180.0)
    ipp = forms.FloatField(label='ipp',min_value=0.1,max_value=2.0)
    simulate = forms.ChoiceField([(False,False),(True,True)])

class RapidObservationForm(forms.ModelForm):
    class Meta:
        model = PhotObs
        fields = ('cadence','jitter','start_obs','stop_obs','airmass_limit','ipp','rapid_mode','simulate')
    start_obs = forms.DateTimeField(label='start_obs',input_formats=["%Y-%m-%dT%H:%M:%S"])
    stop_obs = forms.DateTimeField(label='stop_obs',input_formats=["%Y-%m-%dT%H:%M:%S"])
    airmass_limit = forms.FloatField(label='airmass_limit',min_value=1.0,max_value=2.2)
    ipp = forms.FloatField(label='ipp',min_value=0.1,max_value=2.0)
    rapid_mode = forms.ChoiceField([(False,False),(True,True)])
    simulate = forms.ChoiceField([(False,False),(True,True)])
    
class ExposureSetForm(forms.ModelForm):
    class Meta:
        model = ExposureSet
        fields = ('inst_filter', 'exp_time', 'n_exp',)
    n_exp = forms.IntegerField(label='n_exp',min_value=0)

class AccountForm(forms.ModelForm):
    class Meta:
        model = ProjectUser
        fields = ('handle', 'affiliation', 'email', 'lco_observer_id', 'token')