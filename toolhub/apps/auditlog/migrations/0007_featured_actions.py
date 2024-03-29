# Generated by Django 2.2.17 on 2021-08-07 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auditlog', '0006_backfill_params'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logentry',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(0, 'created'), (1, 'updated'), (2, 'deleted'), (3, 'added to'), (4, 'removed from'), (5, 'hid'), (6, 'revealed'), (7, 'patrolled'), (8, 'featured'), (9, 'unfeatured')], db_index=True, verbose_name='action'),
        ),
    ]
