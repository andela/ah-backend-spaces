# Generated by Django 2.0.6 on 2018-08-03 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_merge_20180803_0959'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_account_verfied',
        ),
    ]
