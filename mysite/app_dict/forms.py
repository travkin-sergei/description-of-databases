# app_dict/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import DimDictionary, LinkDictionaryName, DimCategory


class DimDictionaryForm(forms.ModelForm):
    """Форма для основной модели словаря"""

    class Meta:
        model = DimDictionary
        fields = ['name', 'category', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Введите название словаря'),
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Введите описание словаря'),
                'rows': 4
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': _('Название словаря'),
            'category': _('Категория'),
            'description': _('Описание'),
            'is_active': _('Активен'),
        }


class DictionaryWithSynonymsForm(forms.ModelForm):
    """
    Комбинированная форма для словаря и его синонимов.
    Работает с существующей моделью без добавления новых полей.
    """
    # Поле для хранения синонимов в формате JSON (скрытое)
    synonyms_json = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = DimDictionary
        fields = ['name', 'category', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Введите название словаря'),
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Введите описание словаря'),
                'rows': 4
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': _('Название словаря'),
            'category': _('Категория'),
            'description': _('Описание'),
            'is_active': _('Активен'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Заполняем категории только активными
        self.fields['category'].queryset = DimCategory.objects.filter(is_active=True)

        # При редактировании заполняем синонимы
        if self.instance.pk:
            synonyms = list(self.instance.synonyms.values_list('synonym', flat=True))
            import json
            self.initial['synonyms_json'] = json.dumps(synonyms)

    def clean_synonyms_json(self):
        """Валидация JSON с синонимами"""
        synonyms_json = self.cleaned_data.get('synonyms_json')
        if synonyms_json:
            try:
                import json
                synonyms = json.loads(synonyms_json)
                if not isinstance(synonyms, list):
                    raise forms.ValidationError(_('Неверный формат данных'))

                # Удаляем пустые синонимы и дубликаты
                cleaned_synonyms = []
                seen = set()
                for synonym in synonyms:
                    if isinstance(synonym, str):
                        synonym_clean = synonym.strip()
                        if synonym_clean and synonym_clean not in seen:
                            cleaned_synonyms.append(synonym_clean)
                            seen.add(synonym_clean)

                return cleaned_synonyms
            except Exception as e:
                raise forms.ValidationError(_('Ошибка обработки синонимов: %(error)s') % {'error': str(e)})
        return []

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        category = cleaned_data.get('category')

        # Проверка уникальности пары name + category (учитывая редактирование)
        if name and category:
            qs = DimDictionary.objects.filter(name=name, category=category)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError({
                    'name': _('Словарь с таким названием уже существует в выбранной категории')
                })

        return cleaned_data

    def save(self, commit=True):
        """Сохранение словаря и его синонимов"""
        # Сохраняем основной словарь
        dictionary = super().save(commit=commit)

        if commit:
            # При редактировании удаляем старые синонимы
            if self.instance.pk:
                LinkDictionaryName.objects.filter(name=self.instance).delete()

            # Сохраняем новые синонимы
            synonyms = self.cleaned_data.get('synonyms_json', [])
            for synonym in synonyms:
                LinkDictionaryName.objects.create(
                    name=dictionary,
                    synonym=synonym
                )

        return dictionary