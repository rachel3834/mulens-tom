# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-29 22:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tom', '0012_auto_20180304_1845'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacilityAperture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('code', models.CharField(max_length=4, verbose_name='Name')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='allowed_apertures',
            field=models.ManyToManyField(blank=True, to='tom.FacilityAperture'),
        ),
    ]
