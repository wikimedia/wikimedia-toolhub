# Generated by Django 2.2.24 on 2021-11-25 14:03

from django.db import migrations
import toolhub.fields


class Migration(migrations.Migration):

    dependencies = [
        ('toolinfo', '0013_update_help_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tool',
            name='tool_type',
            field=toolhub.fields.BlankAsNullCharField(blank=True, choices=[('web app', 'web app'), ('desktop app', 'desktop app'), ('bot', 'bot'), ('gadget', 'gadget'), ('user script', 'user script'), ('command line tool', 'command line tool'), ('coding framework', 'coding framework'), ('lua module', 'lua module'), ('template', 'template'), ('other', 'other')], help_text='The manner in which the tool is used. Select one from the list of options.', max_length=32, null=True),
        ),
    ]