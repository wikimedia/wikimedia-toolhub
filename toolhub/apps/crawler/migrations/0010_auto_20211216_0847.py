# Generated by Django 2.2.24 on 2021-12-16 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0009_runurl_logs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runurl',
            name='tools',
            field=models.ManyToManyField(related_name='crawler_runs', to='toolinfo.Tool'),
        ),
    ]
