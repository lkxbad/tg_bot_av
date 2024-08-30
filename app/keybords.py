# app/keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Основное меню
main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Документы', callback_data='pipi')],
        [InlineKeyboardButton(text='Другое', callback_data='other')]
    ]
)

# Клавиатура для выбора статуса документа
status_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='В работе', callback_data='document'), InlineKeyboardButton(text='Не в работе', callback_data='EXECUTED')],
    [InlineKeyboardButton(text='Другое', callback_data='OTHERS')],
    [InlineKeyboardButton(text='Ввести логин', callback_data='back')]
])