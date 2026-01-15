// static/admin/js/optimized_admin.js
(function($) {
    'use strict';

    $(document).ready(function() {
        console.log('Optimized admin JS loaded');

        // Функция для обновления опций в выпадающем списке
        function updateSelectOptions(selectId, baseId, schemaId, tableId) {
            var $select = $(selectId);
            var allOptions = $select.data('all-options') || [];

            if (allOptions.length === 0) {
                // Собираем все опции из select
                $select.find('option').each(function() {
                    var $option = $(this);
                    if ($option.val()) {
                        var text = $option.text();
                        // Парсим текст опции для фильтрации
                        // Формат: Base.Schema.Table.Column (Type)
                        allOptions.push({
                            value: $option.val(),
                            text: text,
                            parts: text.split('.')
                        });
                    }
                });
                $select.data('all-options', allOptions);
            }

            // Фильтруем опции
            var filteredOptions = allOptions.filter(function(option) {
                if (baseId && option.parts[0] !== baseId) return false;
                if (schemaId && option.parts[1] !== schemaId) return false;
                if (tableId && option.parts[2] !== tableId) return false;
                return true;
            });

            // Обновляем select
            $select.empty().append('<option value="">---------</option>');
            filteredOptions.forEach(function(option) {
                $select.append($('<option>', {
                    value: option.value,
                    text: option.text
                }));
            });
        }

        // Назначаем обработчики для фильтров
        $('#main-filter-base, #main-filter-schema, #main-filter-table').change(function() {
            var baseId = $('#main-filter-base').val();
            var schemaId = $('#main-filter-schema').val();
            var tableId = $('#main-filter-table').val();
            updateSelectOptions('#main-select', baseId, schemaId, tableId);
        });

        $('#sub-filter-base, #sub-filter-schema, #sub-filter-table').change(function() {
            var baseId = $('#sub-filter-base').val();
            var schemaId = $('#sub-filter-schema').val();
            var tableId = $('#sub-filter-table').val();
            updateSelectOptions('#sub-select', baseId, schemaId, tableId);
        });

        // Инициализация при загрузке
        updateSelectOptions('#main-select', null, null, null);
        updateSelectOptions('#sub-select', null, null, null);
    });

})(django.jQuery || jQuery);