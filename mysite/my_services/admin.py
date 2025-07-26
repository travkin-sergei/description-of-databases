from django.contrib import admin

from .models import (
    DimServicesTypes, DimServices, DimServicesName,
    DimRoles, LinkResponsiblePerson, LinkServicesTable,
    DimTechStack, DimLink, LinkLink, LinkServicesServices
)


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
    model = LinkLink
    extra = 0
    fields = ('link', 'stage')  # Укажите поля, которые хотите отобразить
    show_change_link = True
    raw_id_fields = ('link', 'stage')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Убедитесь, что все поля DimLink отображаются
        formset.form.base_fields['link'].queryset = DimLink.objects.all()
        return formset


# ——————— ModelAdmins ———————
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
        LinkLinkInline,
    ]
    autocomplete_fields = ('type',)


@admin.register(DimServicesTypes)
class DimServicesTypesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


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
    list_display = ('link_name', 'stack', 'link',)
    search_fields = ('link_name', 'link', 'description')
    ordering = ('link_name',)


@admin.register(LinkLink)
class LinkLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'services', 'link', 'stage')
    list_filter = ('services', 'stage')
    search_fields = ('services__alias', 'link__link_name', 'stage__name')
    ordering = ('services',)
    autocomplete_fields = ('services', 'link', 'stage')


@admin.register(LinkServicesServices)
class LinkServicesServicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'main', 'sub', 'created_at', 'updated_at')
    search_fields = (
        'main__alias',
        'main__dimservicesname__name',
        'sub__alias',
        'sub__dimservicesname__name',
    )
    list_filter = ('created_at', 'updated_at')
    autocomplete_fields = ('main', 'sub')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'main', 'main__type',
            'sub', 'sub__type'
        )
