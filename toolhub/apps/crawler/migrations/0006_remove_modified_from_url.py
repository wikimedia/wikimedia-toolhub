# Generated by Django 2.2.17 on 2020-11-20 00:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0005_rename_crawlerrun_to_run'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='url',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='url',
            name='modified_date',
        ),
    ]
