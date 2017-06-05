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
        fields = ('cadence','jitter','start_obs','stop_obs','airmass_limit')
    start_obs = forms.DateTimeField(label='start_obs',input_formats=["%Y-%m-%dT%H:%M:%S"])
    stop_obs = forms.DateTimeField(label='stop_obs',input_formats=["%Y-%m-%dT%H:%M:%S"])
    airmass_limit = forms.FloatField(label='airmass_limit',min_value=1.0,max_value=2.2)

class ExposureSetForm(forms.ModelForm):
    class Meta:
        model = ExposureSet
        fields = ('inst_filter', 'exp_time', 'n_exp',)

class AccountForm(forms.ModelForm):
    class Meta:
        model = ProjectUser
        fields = ('handle', 'affiliation', 'email', 'lco_observer_id', 'lco_observer_pswd')