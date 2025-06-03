from datetime import datetime, timedelta


def get_cron(cron: str) -> str:
    """
    Расшифровка Cron выражения
    """
    # Разделяем cron-выражение на части
    parts = cron.split()

    # Если длина равна 5, добавляем '*' в начало
    if len(parts) == 5:
        parts.insert(0, '*')

    # Проверяем, что длина теперь равна 6
    if len(parts) != 6:
        return "Неверное cron-выражение"

    second, minute, hour, day_of_month, month, day_of_week = parts

    # Создаем текстовое представление
    text_representation = []

    # Обработка секунд
    if second == '*' or second == '0':
        second = '00'
    elif ',' in second:
        minutes = minute.split(',')
        text_representation.append(f"в {', '.join(minutes)}")

    # Обработка минут
    if minute == '*' or minute == '0':
        minute = '00'

    # Обработка часов
    if hour == '*' or hour == '0':
        text_representation.append(f"00:{minute}:{second}")
    elif hour.startswith('*/'):
        text_representation.append(f"{hour[2:]}:{minute}:{second}")
    else:
        text_representation.append(f"{hour}:{minute}:{second}")

    # Обработка дней месяца
    if day_of_month == '*' or day_of_month == '?':
        pass
    else:
        text_representation.append(f"в {day_of_month} день месяца")

    # Обработка месяцев
    if month == '*':
        text_representation.append("")
    elif month.startswith('*/'):
        interval = month[2:]
        text_representation.append(f"каждые {interval} месяца")
    else:
        text_representation.append(f"в {month} месяц")

    # Обработка дней недели
    if day_of_week == '*' or day_of_week == '7/7':
        text_representation.append("")
    else:
        days_mapping = {
            'MON': 'понедельник',
            'TUE': 'вторник',
            'WED': 'среду',
            'THU': 'четверг',
            'FRI': 'пятницу',
            'SAT': 'субботу',
            'SUN': 'воскресенье'
        }

        days_list = day_of_week.split(',')
        days_text = [days_mapping[day] for day in days_list if day in days_mapping]
        text_representation.append(f"в {', '.join(days_text)}")

    return '\n'.join(text_representation)


# Пример использования


print(get_cron('0 38 22 ? * FRI'))
