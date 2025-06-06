from django.contrib import admin
from .models import (
    DimServicesTypes, DimServices, DimServicesName,
    DimRoles, LinkResponsiblePerson, LinkServicesTable,
    DimTechStack, LinkGit, Swagger
)


# ——————— Inlines ———————

class DimServicesNameInline(admin.TabularInline):
    model = DimServicesName
    extra = 1
    fields = ('name',)
    show_change_link = True


class LinkResponsiblePersonInline(admin.TabularInline):
    model = LinkResponsiblePerson
    extra = 1
    fields = ('role', 'name')
    show_change_link = True
    raw_id_fields = ('role', 'name')


class LinkServicesTableInline(admin.TabularInline):
    model = LinkServicesTable
    extra = 1
    fields = ('table',)
    show_change_link = True
    raw_id_fields = ('table',)


class LinkGitInline(admin.TabularInline):
    model = LinkGit
    fk_name = 'services'
    extra = 1
    fields = ('stack', 'name', 'link_name', 'link', 'description')
    show_change_link = True
    raw_id_fields = ('stack', 'name')


class SwaggerInline(admin.TabularInline):
    model = Swagger
    extra = 1
    fields = ('swagger', 'stage')
    show_change_link = True


# ——————— ModelAdmins ———————

@admin.register(DimServicesTypes)
class DimServicesTypesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(DimServices)
class DimServicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'alias', 'type', 'description')
    list_filter = ('type',)
    search_fields = ('alias', 'description', 'dimservicesname__name')
    ordering = ('alias',)
    inlines = [
        DimServicesNameInline,
        LinkResponsiblePersonInline,
        LinkServicesTableInline,
        LinkGitInline,
        SwaggerInline,
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
        'name__username',
        'name__first_name',
        'name__last_name',
    )
    ordering = ('service',)
    autocomplete_fields = ('role',)
    raw_id_fields = ('service', 'name')


@admin.register(LinkServicesTable)
class LinkServicesTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'table')
    list_filter = ('service',)
    search_fields = ('service__alias', 'table__name')
    ordering = ('service',)
    raw_id_fields = ('service', 'table')


@admin.register(DimTechStack)
class DimTechStackAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(LinkGit)
class LinkGitAdmin(admin.ModelAdmin):
    list_display = ('id', 'services', 'stack', 'name', 'link_name', 'link')
    list_filter = ('services', 'stack')
    search_fields = ('link_name', 'name__alias', 'services__alias')
    ordering = ('link_name',)
    raw_id_fields = ('stack', 'name')
    autocomplete_fields = ('services',)


@admin.register(Swagger)
class SwaggerAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'swagger',)
    list_filter = ('service',)
    search_fields = ('service__alias', 'swagger',)
    ordering = ('service',)
    autocomplete_fields = ('service',)
    list_select_related = ('service',)
