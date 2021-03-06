# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-09 13:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('phone', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=256)),
                ('city', models.CharField(max_length=256)),
                ('gender', models.BooleanField(default=False)),
                ('age', models.IntegerField()),
            ],
        ),
    ]
