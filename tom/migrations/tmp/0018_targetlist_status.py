# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-04-08 23:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tom', '0017_projectuser_email_notifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetlist',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]