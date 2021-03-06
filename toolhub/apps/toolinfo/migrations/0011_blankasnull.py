# Generated by Django 2.2.17 on 2021-03-28 21:02

import django.core.validators
from django.db import migrations
import toolhub.apps.toolinfo.models
import toolhub.apps.toolinfo.validators
import toolhub.fields


class Migration(migrations.Migration):

    dependencies = [
        ('toolinfo', '0010_tool_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tool',
            name='_language',
            field=toolhub.apps.toolinfo.models.BlankAsNullCharField(blank=True, help_text='The language in which this toolinfo record is written. If not set, the default value is English. Use ISO 639 language codes.', max_length=16, null=True, validators=[django.core.validators.RegexValidator(regex='^(x-.*|[A-Za-z]{2,3}(-.*)?)$')]),
        ),
        migrations.AlterField(
            model_name='tool',
            name='_schema',
            field=toolhub.apps.toolinfo.models.BlankAsNullCharField(blank=True, help_text='A URI identifying the jsonschema for this toolinfo.json record. This should be a short uri containing only the name and revision at the end of the URI path.', max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='tool',
            name='api_url',
            field=toolhub.apps.toolinfo.models.BlankAsNullTextField(blank=True, help_text="A link to the tool's API, if available.", max_length=2047, null=True, validators=[django.core.validators.URLValidator(schemes=['http', 'https'])]),
        ),
        migrations.AlterField(
            model_name='tool',
            name='author',
            field=toolhub.apps.toolinfo.models.BlankAsNullCharField(blank=True, help_text='The primary tool developer.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='tool',
            name='available_ui_languages',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list, help_text="The language(s) the tool's interface has been translated into. Use ISO 639 language codes like `zh` and `scn`. If not defined it is assumed the tool is only available in English."),
        ),
        migrations.AlterField(
            model_name='tool',
            name='bot_username',
            field=toolhub.apps.toolinfo.models.BlankAsNullCharField(blank=True, help_text="If the tool is a bot, the Wikimedia username of the bot. Do not include 'User:' or similar prefixes.", max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='tool',
            name='bugtracker_url',
            field=toolhub.apps.toolinfo.models.BlankAsNullTextField(blank=True, help_text="A link to the tool's bug tracker on GitHub, Bitbucket, Phabricator, etc.", max_length=2047, null=True, validators=[django.core.validators.URLValidator(schemes=['http', 'https'])]),
        ),
        migrations.AlterField(
            model_name='tool',
            name='developer_docs_url',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list, help_text="A link to the tool's developer documentation, if available."),
        ),
        migrations.AlterField(
            model_name='tool',
            name='feedback_url',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list, help_text="A link to location where the tool's user can leave feedback."),
        ),
        migrations.AlterField(
            model_name='tool',
            name='for_wikis',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list, help_text="A string or array of strings describing the wiki(s) this tool can be used on. Use hostnames such as `zh.wiktionary.org`. Use asterisks as wildcards. For example, `*.wikisource.org` means 'this tool works on all Wikisource wikis.' `*` means 'this works on all wikis, including Wikimedia wikis.'"),
        ),
        migrations.AlterField(
            model_name='tool',
            name='icon',
            field=toolhub.apps.toolinfo.models.BlankAsNullCharField(blank=True, help_text='A link to a Wikimedia Commons file description page for an icon that depicts the tool.', max_length=2047, null=True, validators=[django.core.validators.RegexValidator(regex='^https://commons\\.wikimedia\\.org/wiki/File:.+\\..+$')]),
        ),
        migrations.AlterField(
            model_name='tool',
            name='keywords',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='tool',
            name='license',
            field=toolhub.apps.toolinfo.models.BlankAsNullCharField(blank=True, help_text="The software license the tool code is available under. Use a standard SPDX license identifier like 'GPL-3.0-or-later'.", max_length=255, null=True, validators=[toolhub.apps.toolinfo.validators.validate_spdx]),
        ),
        migrations.AlterField(
            model_name='tool',
            name='openhub_id',
            field=toolhub.apps.toolinfo.models.BlankAsNullCharField(blank=True, help_text='The project ID on OpenHub. Given a URL of https://openhub.net/p/foo, the project ID is `foo`.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='tool',
            name='privacy_policy_url',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list, help_text="A link to the tool's privacy policy, if available."),
        ),
        migrations.AlterField(
            model_name='tool',
            name='replaced_by',
            field=toolhub.apps.toolinfo.models.BlankAsNullTextField(blank=True, help_text='If this tool is deprecated, this parameter should be used to link to the replacement tool.', max_length=2047, null=True, validators=[django.core.validators.URLValidator(schemes=['http', 'https'])]),
        ),
        migrations.AlterField(
            model_name='tool',
            name='repository',
            field=toolhub.apps.toolinfo.models.BlankAsNullCharField(blank=True, help_text='A link to the repository where the tool code is hosted.', max_length=2047, null=True),
        ),
        migrations.AlterField(
            model_name='tool',
            name='sponsor',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list, help_text="Organization(s) that sponsored the tool's development."),
        ),
        migrations.AlterField(
            model_name='tool',
            name='subtitle',
            field=toolhub.apps.toolinfo.models.BlankAsNullCharField(blank=True, help_text='Longer than the full title but shorter than the description. It should add some additional context to the title.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='tool',
            name='technology_used',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list, help_text='A string or array of strings listing technologies (programming languages, development frameworks, etc.) used in creating the tool.'),
        ),
        migrations.AlterField(
            model_name='tool',
            name='tool_type',
            field=toolhub.apps.toolinfo.models.BlankAsNullCharField(blank=True, choices=[('web app', 'web app'), ('desktop app', 'desktop app'), ('bot', 'bot'), ('gadget', 'gadget'), ('user script', 'user script'), ('command line tool', 'command line tool'), ('coding framework', 'coding framework'), ('other', 'other')], help_text='The manner in which the tool is used. Select one from the list of options.', max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='tool',
            name='translate_url',
            field=toolhub.apps.toolinfo.models.BlankAsNullTextField(blank=True, help_text="A link to the tool's translation interface.", max_length=2047, null=True, validators=[django.core.validators.URLValidator(schemes=['http', 'https'])]),
        ),
        migrations.AlterField(
            model_name='tool',
            name='url_alternates',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list, help_text='Alternate links to the tool or install documentation in different natural languages.'),
        ),
        migrations.AlterField(
            model_name='tool',
            name='user_docs_url',
            field=toolhub.fields.JSONSchemaField(blank=True, default=list, help_text="A link to the tool's user documentation, if available."),
        ),
    ]
