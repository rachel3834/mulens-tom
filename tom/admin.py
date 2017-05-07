# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import ProjectUser, Project, Target, TargetName
from .models import TargetList, PhotObs, ExposureSet

admin.site.register(ProjectUser)
admin.site.register(Project)
admin.site.register(Target)
admin.site.register(TargetName)
admin.site.register(TargetList)
admin.site.register(ExposureSet)
admin.site.register(PhotObs)