# -*- coding: utf-8 -*-
"""
Created on Mon May  1 14:23:30 2017

@author: rstreet
"""

from tom.models import *
from django import forms

class AddTargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ('ra','dec')

class AddTargetNameForm(forms.ModelForm):
    class Meta:
        model = TargetName
        fields = ('name',)

class AddObservationForm(forms.ModelForm):
    class Meta:
        model = PhotObs
        fields = ('filters','exp_times','n_exp','cadence','jitter',
                  'start_obs','stop_obs',)

class SelectTargetNameForm(forms.ModelForm):
    class Meta:
        model = TargetName
        fields = ('name',)

class SelectTargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ('ra','dec',)
