# Generated by Django 4.1 on 2024-09-03 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataSources',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='запись активна')),
                ('task', models.URLField(verbose_name='Cсылка на задачу в Jira')),
                ('slag', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('link_sources', models.URLField(blank=True, null=True)),
                ('doc_regulatory', models.URLField(blank=True, null=True)),
                ('name_sources', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name': '01 Список источников',
                'verbose_name_plural': '01 Список источников',
                'db_table': 'source_data',
            },
        ),
    ]
