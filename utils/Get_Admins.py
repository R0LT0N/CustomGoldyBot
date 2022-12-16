# - *- coding: utf- 8 - *-
import configparser

# Получение администраторов бота
def get_admins():
    parser = configparser.ConfigParser()
    parser.read("config.ini", encoding="utf-8")
    admins = parser['ADMIN']['admin_id'].strip().replace(" ", "")

    if "," in admins:
        admins = admins.split(",")
    else:
        if len(admins) >= 1:
            admins = [admins]
        else:
            admins = []

    while "" in admins: admins.remove("")
    while " " in admins: admins.remove(" ")
    while "\r" in admins: admins.remove("\r")
    while "\n" in admins: admins.remove("\n")

    admins = list(map(int, admins))

    return admins
