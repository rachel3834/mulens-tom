# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-25 16:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tom', '0014_auto_20180924_2325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exposureset',
            name='inst_filter',
            field=models.CharField(choices=[('SDSS-i', 'SDSS-i'), ('SDSS-r', 'SDSS-r'), ('SDSS-g', 'SDSS-g'), ('Pan-STARRS-Z', 'Pan-STARRS-Z'), ('Bessell-V', 'Bessell-V'), ('Bessell-R', 'Bessell-R'), ('Cousins-Ic', 'Cousins-Ic'), ('None', 'None')], default='SDSS-i', max_length=15, verbose_name='Filter'),
        ),
    ]