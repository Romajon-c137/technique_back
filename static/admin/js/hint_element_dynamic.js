(function ($) {
    'use strict';

    $(document).ready(function () {
        console.log('Hint element dynamic fields script loaded');

        // Функция для показа/скрытия полей в зависимости от типа элемента
        function toggleHintElementFields(row) {
            console.log('Toggling fields for row');

            // Находим select с типом элемента
            var elementTypeSelect = row.find('select[id$="-element_type"]');
            if (elementTypeSelect.length === 0) {
                console.log('Element type select not found');
                return;
            }

            var elementType = elementTypeSelect.val();
            console.log('Element type:', elementType);

            // Находим поля
            var textField = row.find('textarea[id$="-text_content"]').closest('td');
            var imageField = row.find('input[id$="-image"]').closest('td');
            var videoField = row.find('input[id$="-video_url"]').closest('td');

            console.log('Fields found:', {
                text: textField.length,
                image: imageField.length,
                video: videoField.length
            });

            // Скрываем все поля по умолчанию
            textField.hide();
            imageField.hide();
            videoField.hide();

            // Очищаем неиспользуемые поля
            if (elementType !== 'text') {
                row.find('textarea[id$="-text_content"]').val('');
            }
            if (elementType !== 'video') {
                row.find('input[id$="-video_url"]').val('');
            }

            // Показываем только нужное поле
            if (elementType === 'text') {
                textField.show();
                console.log('Showing text field');
            } else if (elementType === 'image') {
                imageField.show();
                console.log('Showing image field');
            } else if (elementType === 'video') {
                videoField.show();
                console.log('Showing video field');
            }
        }

        // Применяем к существующим строкам при загрузке страницы
        function initializeRows() {
            console.log('Initializing rows');
            $('#hintelement_set-group .form-row').not('.empty-form').each(function () {
                toggleHintElementFields($(this));
            });
        }

        // Инициализация при загрузке
        initializeRows();

        // Обработчик изменения типа элемента
        $(document).on('change', 'select[id$="-element_type"]', function () {
            console.log('Element type changed');
            var row = $(this).closest('.form-row');
            toggleHintElementFields(row);
        });

        // Обработчик добавления новой строки (для Django 3.2+)
        $(document).on('formset:added', function (event, $row, formsetName) {
            console.log('Formset added:', formsetName);
            if (formsetName.includes('hintelement')) {
                toggleHintElementFields($row);
            }
        });

        // Альтернативный обработчик для старых версий Django
        $('.add-row a').on('click', function () {
            setTimeout(function () {
                console.log('Add row clicked');
                initializeRows();
            }, 100);
        });
    });
})(django.jQuery);
