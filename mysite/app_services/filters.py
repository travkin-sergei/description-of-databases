# app_services/filters.py
import django_filters
from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView

from app_auth.models import MyProfile
from app_dbm.models import DimStage

from .models import (
    DimServices, DimServicesTypes, DimRoles, DimTechStack, LinksUrlService,
)


class DimServicesFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        field_name='alias',
        lookup_expr='icontains',
        label='Сервис'
    )

    type = django_filters.ModelChoiceFilter(
        queryset=DimServicesTypes.objects.all(),
        field_name='type',
        label='Тип',
        empty_label="Любой"
    )

    user = django_filters.CharFilter(
        method='filter_by_user_name',
        label='Пользователь (логин)'
    )

    role = django_filters.ModelChoiceFilter(
        queryset=DimRoles.objects.all(),
        method='filter_by_role',
        label='Роль',
        empty_label="Любая"
    )

    class Meta:
        model = DimServices
        fields = ['search', 'type', 'user', 'role']

    def filter_by_user_name(self, queryset, name, value):
        if not value or not value.strip():
            return queryset

        # Ищем пользователей по имени пользователя (username)
        # MyProfile имеет связь с User через поле user
        profile_ids = MyProfile.objects.filter(
            user__username__icontains=value
        ).values_list('id', flat=True)

        return queryset.filter(
            linkresponsibleperson__name_id__in=profile_ids
        ).distinct()

    def filter_by_role(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            linkresponsibleperson__role=value
        ).distinct()


class LinksUrlServiceFilter(django_filters.FilterSet):
    """Фильтры ссылок сервисов."""

    # Фильтр по URL через связанную модель DimUrl
    url = django_filters.CharFilter(
        field_name='url__url',  # доступ к полю url в модели DimUrl
        lookup_expr='icontains',
        label='URL содержит'
    )

    link_name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Название ссылки содержит'
    )

    description = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Описание содержит'
    )

    # Фильтры по ForeignKey полям
    stack = django_filters.ModelChoiceFilter(
        queryset=DimTechStack.objects.all(),
        label='Технологический стек'
    )

    stage = django_filters.ModelChoiceFilter(
        queryset=DimStage.objects.all(),
        label='Стадия проекта'
    )

    service = django_filters.ModelChoiceFilter(
        queryset=DimServices.objects.all(),
        label='Сервис'
    )

    class Meta:
        model = LinksUrlService
        fields = ['url', 'link_name', 'stack', 'stage', 'service', 'description']


class ServiceUserView(LoginRequiredMixin, FilterView):
    """Отношение User к Service - правильная реализация FilterView"""

    model = DimServices
    filterset_class = DimServicesFilter
    template_name = 'app_services/services-user.html'
    context_object_name = 'services'
    paginate_by = 20

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)

        # Безопасная обработка kwargs['data']
        data = kwargs.get('data')
        if data is not None:
            data = data.copy()  # делаем mutable копию
            # Удаляем пустые значения
            for key in list(data.keys()):
                if data[key] == '':
                    del data[key]
            kwargs['data'] = data

        return kwargs

    def get_queryset(self):
        """Получение queryset с предзагрузкой"""
        queryset = super().get_queryset()
        return queryset.prefetch_related(
            'type',
            'dimservicesname_set',
            'linkresponsibleperson_set__role',
            'linkresponsibleperson_set__name'
        ).order_by('alias')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Отладочная информация
        context['debug_info'] = {
            'total_count': DimServices.objects.count(),
            'filtered_count': self.object_list.count(),
            'form_data': dict(self.request.GET),
        }

        # Сохраняем параметры фильтрации для пагинации
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']

        # Очищаем пустые значения для query_string
        for key in list(get_params.keys()):
            if get_params[key] == '':
                del get_params[key]

        if get_params:
            context['query_string'] = get_params.urlencode()

        return context
