# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-29 22:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tom', '0013_auto_20180529_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facilityaperture',
            name='code',
            field=models.CharField(max_length=4, verbose_name='Code'),
        ),
    ]