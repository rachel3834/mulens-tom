# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import User, Project, Target, TargetName
from .models import TargetList, PhotObs

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Target)
admin.site.register(TargetName)
admin.site.register(TargetList)
admin.site.register(PhotObs)