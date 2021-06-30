# Generated by Django 2.2.17 on 2021-06-02 20:02

from django.db import migrations
import toolhub.apps.toolinfo.validators
import toolhub.fields


class Migration(migrations.Migration):

    dependencies = [
        ('toolinfo', '0012_language_validators'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tool',
            name='developer_docs_url',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list, help_text="A link to the tool's developer documentation, if available.", validators=[toolhub.apps.toolinfo.validators.validate_url_mutilingual_list]),
        ),
        migrations.AlterField(
            model_name='tool',
            name='feedback_url',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list, help_text="A link to location where the tool's user can leave feedback.", validators=[toolhub.apps.toolinfo.validators.validate_url_mutilingual_list]),
        ),
        migrations.AlterField(
            model_name='tool',
            name='privacy_policy_url',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list, help_text="A link to the tool's privacy policy, if available.", validators=[toolhub.apps.toolinfo.validators.validate_url_mutilingual_list]),
        ),
        migrations.AlterField(
            model_name='tool',
            name='url_alternates',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list, help_text='Alternate links to the tool or install documentation in different natural languages.', validators=[toolhub.apps.toolinfo.validators.validate_url_mutilingual_list]),
        ),
        migrations.AlterField(
            model_name='tool',
            name='user_docs_url',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list, help_text="A link to the tool's user documentation, if available.", validators=[toolhub.apps.toolinfo.validators.validate_url_mutilingual_list]),
        ),
    ]