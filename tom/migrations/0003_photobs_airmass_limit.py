# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-05 18:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tom', '0002_auto_20170515_2205'),
    ]

    operations = [
        migrations.AddField(
            model_name='photobs',
            name='airmass_limit',
            field=models.FloatField(blank=True, default=1.5, verbose_name='Airmass limit'),
        ),
    ]
