# Generated by Django 2.2.17 on 2021-06-27 16:01

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import toolhub.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('toolinfo', '0013_update_help_text'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ToolList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('title', models.CharField(help_text='Title of this list', max_length=255)),
                ('description', toolhub.fields.BlankAsNullTextField(blank=True, help_text="Description of the list's theme or contents.", max_length=65535, null=True)),
                ('icon', toolhub.fields.BlankAsNullCharField(blank=True, help_text='A link to a Wikimedia Commons file description page for an icon that depicts the list.', max_length=2047, null=True, validators=[django.core.validators.RegexValidator(regex='^https://commons\\.wikimedia\\.org/wiki/File:.+\\..+$')])),
                ('favorites', models.BooleanField(default=False, help_text="If true, this list is a collection of the owning user's'favorite' tools.")),
                ('published', models.BooleanField(default=False, help_text='If true, this list is visible to everyone.')),
                ('featured', models.BooleanField(default=False, help_text='If true, this list has been marked as featured.')),
                ('created_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lists', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ToolListItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField(default=0, help_text='Position of this tool in the list.')),
                ('added_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('tool', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='toolinfo.Tool')),
                ('toollist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lists.ToolList')),
            ],
            options={
                'ordering': ('order', 'added_date'),
            },
        ),
        migrations.AddField(
            model_name='toollist',
            name='tools',
            field=models.ManyToManyField(through='lists.ToolListItem', to='toolinfo.Tool'),
        ),
    ]
