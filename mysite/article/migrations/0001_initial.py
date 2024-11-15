# Generated by Django 5.1.2 on 2024-11-06 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='запись активна')),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True, verbose_name='Слаг')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
            ],
            options={
                'verbose_name': '01 Статья',
                'verbose_name_plural': '01 Статьи',
                'db_table': 'doc_article',
            },
        ),
    ]
