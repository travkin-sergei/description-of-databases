# app_services/admin.py
from django.contrib import admin
from .models import (
    DimServicesTypes, DimServices, DimServicesName,
    DimRoles, LinkResponsiblePerson, LinkServicesTable,
    DimTechStack, LinksUrlService, LinkServicesServices,
    DimServicesNameType, LinkDoc  # Добавлен LinkDoc
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
    fields = ('name', 'type')
    show_change_link = True
    autocomplete_fields = ('type',)


class LinkResponsiblePersonInline(admin.TabularInline):
    model = LinkResponsiblePerson
    extra = 0
    fields = ('role', 'name')
    show_change_link = True
    raw_id_fields = ('name',)
    autocomplete_fields = ('role',)


class LinkServicesTableInline(admin.TabularInline):
    model = LinkServicesTable
    extra = 0
    fields = ('table',)
    show_change_link = True
    raw_id_fields = ('table',)


class LinksUrlServiceInline(admin.TabularInline):
    model = LinksUrlService
    extra = 0
    fields = ('url', 'link_name', 'stage', 'stack', 'description')
    show_change_link = True
    autocomplete_fields = ('url', 'stage', 'stack')


class LinkDocInline(admin.TabularInline):  # Новый инлайн для связи документов
    model = LinkDoc
    extra = 0
    fields = ('doc',)
    show_change_link = True
    autocomplete_fields = ('doc',)


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
        LinkDocInline,
        LinkServicesTableInline,
        LinksUrlServiceInline,
    ]
    autocomplete_fields = ('type',)


@admin.register(DimServicesName)
class DimServicesNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'alias', 'name', 'type')
    search_fields = ('name', 'alias__alias')
    ordering = ('name',)
    autocomplete_fields = ('alias', 'type')


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


@admin.register(LinksUrlService)
class LinksUrlServiceAdmin(admin.ModelAdmin):
    list_display = ('url', 'service', 'link_name', 'stage', 'stack')
    list_filter = ('service', 'stage', 'stack')
    search_fields = ('url__url', 'link_name', 'service__alias', 'description')
    ordering = ('url',)
    autocomplete_fields = ('url', 'service', 'stage', 'stack')


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


@admin.register(DimServicesNameType)
class DimServicesNameTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(LinkDoc)
class LinkDocAdmin(admin.ModelAdmin):
    list_display = ('id', 'services', 'doc')
    list_filter = ('services',)
    search_fields = ('services__alias', 'doc__number', 'doc__description')
    ordering = ('services', 'doc')
    autocomplete_fields = ('services', 'doc')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('services', 'doc')
