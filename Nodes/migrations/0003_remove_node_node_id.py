# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-04 00:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Nodes', '0002_auto_20160104_0016'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='node',
            name='node_id',
        ),
    ]
