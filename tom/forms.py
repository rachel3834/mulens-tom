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
        fields = ('cadence','jitter','group_type',
                  'start_obs','stop_obs',)

class ExposureSetForm(forms.ModelForm):
    class Meta:
        model = ExposureSet
        fields = ('inst_filter', 'exp_time', 'n_exp',)