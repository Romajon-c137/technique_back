/**
 * Динамическое отображение полей расписания в зависимости от типа ТО
 */
(function () {
    'use strict';

    function updateScheduleFields() {
        const typeField = document.getElementById('id_type');
        if (!typeField) return;

        const type = typeField.value;

        // Поля расписания
        const scheduledDateRow = document.querySelector('.field-scheduled_date');
        const weekdayRow = document.querySelector('.field-weekday');
        const dayOfMonthRow = document.querySelector('.field-day_of_month');

        if (!scheduledDateRow || !weekdayRow || !dayOfMonthRow) return;

        // Скрыть все поля по умолчанию
        scheduledDateRow.style.display = 'none';
        weekdayRow.style.display = 'none';
        dayOfMonthRow.style.display = 'none';

        // Показать нужные поля в зависимости от типа
        switch (type) {
            case 'one_time':
                scheduledDateRow.style.display = '';
                break;
            case 'weekly':
                weekdayRow.style.display = '';
                break;
            case 'monthly':
                dayOfMonthRow.style.display = '';
                break;
            case 'daily':
                // Для ежедневного не нужно дополнительных полей
                break;
        }
    }

    // Запускаем при загрузке страницы
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            updateScheduleFields();

            // Добавляем обработчик изменения типа
            const typeField = document.getElementById('id_type');
            if (typeField) {
                typeField.addEventListener('change', updateScheduleFields);
            }
        });
    } else {
        updateScheduleFields();

        const typeField = document.getElementById('id_type');
        if (typeField) {
            typeField.addEventListener('change', updateScheduleFields);
        }
    }
})();
