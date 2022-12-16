# - *- coding: utf- 8 - *-
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from utils.Get_Admins import get_admins

# Проверка на админа
class IsAdmin(BoundFilter):
    async def check(self, message: types.Message):
        if message.from_user.id in get_admins():
            return True
        else:
            return False
