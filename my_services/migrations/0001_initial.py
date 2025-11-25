import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('my_auth', '0003_myprofile_link_profile'),
        ('my_dbm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DimRoles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='запись активна')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': '01 Роли в сервисе.',
                'verbose_name_plural': '01 Роли в сервисах.',
                'db_table': 'my_services"."dim_roles',
                'unique_together': {('name',)},
            },
        ),
        migrations.CreateModel(
            name='DimServicesTypes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='запись активна')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': '02 Типы сервисов.',
                'verbose_name_plural': '02 Типы сервисов.',
                'db_table': 'my_services"."dim_services_type',
                'unique_together': {('name',)},
            },
        ),
        migrations.CreateModel(
            name='DimServices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='запись активна')),
                ('alias', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('type',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='my_services.dimservicestypes')),
            ],
            options={
                'verbose_name': '08 Список сервисов.',
                'verbose_name_plural': '08 Список сервисов.',
                'db_table': 'my_services"."dim_services',
                'unique_together': {('alias', 'type')},
            },
        ),
        migrations.CreateModel(
            name='DimTechStack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='запись активна')),
                ('name', models.CharField()),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': '06 Технология.',
                'verbose_name_plural': '06 Технологии.',
                'db_table': 'my_services"."link_tech_stack',
                'unique_together': {('name',)},
            },
        ),
        migrations.CreateModel(
            name='DimServicesName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='запись активна')),
                ('name', models.CharField(max_length=255)),
                ('alias', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='my_services.dimservices')),
            ],
            options={
                'verbose_name': '03 Синонимы сервисов.',
                'verbose_name_plural': '03 Синонимы сервисов.',
                'db_table': 'my_services"."dim_services_name',
                'unique_together': {('alias', 'name')},
            },
        ),
        migrations.CreateModel(
            name='DimLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='запись активна')),
                ('link', models.URLField(blank=True, null=True)),
                ('link_name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('stage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                            to='my_dbm.dimstage')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                              to='my_services.dimservices')),
                ('stack', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                            to='my_services.dimtechstack')),
            ],
            options={
                'verbose_name': '08 ссылки на репозиторий.',
                'verbose_name_plural': '08 ссылки на репозиторий.',
                'db_table': 'my_services"."dim_link',
                'unique_together': {('link',)},
            },
        ),
        migrations.CreateModel(
            name='LinkResponsiblePerson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='запись активна')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='my_auth.myprofile')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='my_services.dimroles')),
                ('service',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='my_services.dimservices')),
            ],
            options={
                'verbose_name': '04 Ответственные за сервис.',
                'verbose_name_plural': '04 Ответственные за сервис.',
                'db_table': 'my_services"."link_responsible_person',
                'unique_together': {('service', 'role', 'name')},
            },
        ),
        migrations.CreateModel(
            name='LinkServicesServices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='запись активна')),
                ('main', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='my_main',
                                           to='my_services.dimservices')),
                ('sub', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='my_sub',
                                          to='my_services.dimservices')),
            ],
            options={
                'verbose_name': '04 Группировки сервисов.',
                'verbose_name_plural': '04 Группировки сервисов.',
                'db_table': 'my_services"."link_services_services',
                'unique_together': {('main', 'sub')},
            },
        ),
        migrations.CreateModel(
            name='LinkServicesTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='дата изменения')),
                ('is_active', models.BooleanField(default=True, verbose_name='запись активна')),
                ('service',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='my_services.dimservices')),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='my_dbm.linkdbtable')),
            ],
            options={
                'verbose_name': '05 Таблицы сервиса.',
                'verbose_name_plural': '05 Таблицы сервиса.',
                'db_table': 'my_services"."link_service_table',
                'unique_together': {('service', 'table')},
            },
        ),
    ]
