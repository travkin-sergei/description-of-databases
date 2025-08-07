# admin.py
from django.contrib import admin
from .models import (
    DimServicesTypes, DimServices, DimServicesName,
    DimRoles, LinkResponsiblePerson, LinkServicesTable,
    DimTechStack, DimLink, LinkServicesServices, LinkCheckSchedule
)
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler.admin import DjangoJobExecutionAdmin

# Сначала отменяем стандартную регистрацию
admin.site.unregister(DjangoJobExecution)


# Затем регистрируем свою кастомизированную версию (если нужно)
@admin.register(DjangoJobExecution)
class CustomDjangoJobExecutionAdmin(DjangoJobExecutionAdmin):
    list_display = ['id', 'job', 'status', 'run_time', 'duration']
    list_filter = ['status', 'job']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


# ——————— Inlines ———————
class DimServicesNameInline(admin.TabularInline):
    model = DimServicesName
    extra = 0
    fields = ('name',)
    show_change_link = True


class LinkResponsiblePersonInline(admin.TabularInline):
    model = LinkResponsiblePerson
    extra = 0
    fields = ('role', 'name')
    show_change_link = True
    raw_id_fields = ('name',)


class LinkServicesTableInline(admin.TabularInline):
    model = LinkServicesTable
    extra = 0
    fields = ('table',)
    show_change_link = True
    raw_id_fields = ('table',)


class LinkLinkInline(admin.TabularInline):
    model = DimLink
    extra = 0
    fields = ('link', 'link_name', 'stack', 'stage', 'description')
    show_change_link = True


# ——————— ModelAdmins ———————
@admin.register(DimServicesTypes)
class DimServicesTypesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(DimServices)
class DimServicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'alias', 'type',)
    list_filter = ('type',)
    search_fields = ('alias', 'description', 'dimservicesname__name')
    ordering = ('alias',)
    inlines = [
        DimServicesNameInline,
        LinkResponsiblePersonInline,
        LinkServicesTableInline,
        LinkLinkInline,
    ]
    autocomplete_fields = ('type',)


@admin.register(DimServicesName)
class DimServicesNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'alias', 'name')
    search_fields = ('name', 'alias__alias')
    ordering = ('name',)
    autocomplete_fields = ('alias',)


@admin.register(DimRoles)
class DimRolesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(LinkResponsiblePerson)
class LinkResponsiblePersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'role', 'name')
    list_filter = ('service', 'role')
    search_fields = (
        'service__alias',
        'role__name',
        'name__user__username',
        'name__user__first_name',
        'name__user__last_name',
    )
    ordering = ('service',)
    autocomplete_fields = ('service', 'role')
    raw_id_fields = ('name',)


@admin.register(LinkServicesTable)
class LinkServicesTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'table')
    list_filter = ('service',)
    search_fields = ('service__alias', 'table__name')
    ordering = ('service',)
    autocomplete_fields = ('service', 'table')


@admin.register(DimTechStack)
class DimTechStackAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(DimLink)
class DimLinkAdmin(admin.ModelAdmin):
    list_display = ('link', 'link_name', 'last_checked', 'status_code', 'is_active')
    list_filter = ('is_active', 'last_checked', 'service')
    search_fields = ('link', 'link_name')
    readonly_fields = ('last_checked',)

    fieldsets = (
        (None, {
            'fields': ('link', 'link_name', 'description')
        }),
        ('Статус', {
            'fields': ('last_checked', 'status_code', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Связи', {
            'fields': ('stack', 'stage', 'service'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LinkServicesServices)
class LinkServicesServicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'main', 'sub')
    search_fields = (
        'main__alias',
        'main__dimservicesname__name',
        'sub__alias',
        'sub__dimservicesname__name',
    )
    autocomplete_fields = ('main', 'sub')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'main', 'main__type',
            'sub', 'sub__type'
        )


@admin.register(LinkCheckSchedule)
class LinkCheckScheduleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active',)

    def save_model(self, request, obj, form, change):
        from apscheduler.triggers.cron import CronTrigger
        from apscheduler.jobstores.base import JobLookupError
        from .scheduler import scheduler, check_all_links_job

        super().save_model(request, obj, form, change)

        # Удаляем предыдущую задачу, если есть
        try:
            scheduler.remove_job('link_checker')
        except JobLookupError:
            pass

        if obj.is_active:
            parts = obj.cron_expression.split()
            if len(parts) != 7:
                # Можно вывести сообщение об ошибке в админке или лог
                print(f"Ошибка: cron_expression должен содержать 7 частей, а получил {len(parts)}")
                return

            second, minute, hour, day, month, day_of_week, year = parts

            trigger = CronTrigger(
                second=second,
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
                year=year,
            )

            scheduler.add_job(
                check_all_links_job,
                trigger=trigger,
                id='link_checker',
                replace_existing=True,
            )

            obj.next_run = None
            obj.save()

    def run_manually(self, request, queryset):
        from .scheduler import check_all_links_job
        check_all_links_job()
        self.message_user(request, "Проверка ссылок запущена вручную")

    run_manually.short_description = "Запустить проверку сейчас"
