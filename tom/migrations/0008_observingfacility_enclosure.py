# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-13 02:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tom', '0007_auto_20180113_0207'),
    ]

    operations = [
        migrations.AddField(
            model_name='observingfacility',
            name='enclosure',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Enclosure'),
        ),
    ]