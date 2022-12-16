import time
from datetime import datetime

# Получение текущего unix времени
def get_unix(full=False):
    if full:
        return time.time_ns()
    else:
        return int(time.time())


# Получение текущей даты
def get_date():
    this_date = datetime.today().replace(microsecond=0)
    this_date = this_date.strftime("%d.%m.%Y %H_%M_%S")

    return this_date

# Конвертация дней
def convert_day(day):
    day = int(day)
    days = ['день', 'дня', 'дней']

    if day % 10 == 1 and day % 100 != 11:
        count = 0
    elif 2 <= day % 10 <= 4 and (day % 100 < 10 or day % 100 >= 20):
        count = 1
    else:
        count = 2

    return f"{day} {days[count]}"
