# -*- coding: utf-8 -*-
from telebot import types
from data_base import DataBase

# keyboards
# ------------------------------
button_back = types.KeyboardButton(text='Назад')


def get_keyboard_telephone():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button_telephone = types.KeyboardButton(text='Отправить номер телефона', request_contact=True)
    keyboard.add(button_telephone)
    return keyboard


def get_keyboard_menu():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button_add = types.KeyboardButton(text='Записаться на прием')
    button_see = types.KeyboardButton(text='Просмотр записи')
    button_setting = types.KeyboardButton(text='Настройка')
    keyboard.add(button_add, button_see,
                 button_setting)
    return keyboard


def get_keyboard_menu_edit():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button_pet = types.KeyboardButton(text='Редактор Питомцев')
    button_owner = types.KeyboardButton(text='Редактор Пользователя')
    keyboard.add(button_pet, button_owner,
                 button_back)
    return keyboard


def get_keyboard_edit_pet():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button_breed = types.KeyboardButton(text='Порода')
    button_weight = types.KeyboardButton(text='Вес')
    button_info = types.KeyboardButton(text='О питомце')
    keyboard.add(button_breed, button_weight,
                 button_info, button_back)
    return keyboard


def get_keyboard_edit_owner():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button_name = types.KeyboardButton(text='Имя')
    button_first_name = types.KeyboardButton(text='Фамилия')
    button_second_name = types.KeyboardButton(text='Отчество')
    button_address = types.KeyboardButton(text='Адрес проживания')
    button_email = types.KeyboardButton(text='Почта')
    keyboard.add(button_name, button_first_name,
                 button_second_name, button_address,
                 button_email, button_back)
    return keyboard


def get_keyboard_gender():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button_boy = types.KeyboardButton(text='Мальчик')
    button_girl = types.KeyboardButton(text='Девочка')
    keyboard.add(button_boy, button_girl)
    return keyboard


def get_keyboard_date():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    db = DataBase()
    for n in db.get_dates():
        keyboard.add(n)
    db.close()
    return keyboard


def get_keyboard_time(day):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    db = DataBase()
    for n in db.get_times(day):
        keyboard.add(n)
    keyboard.add(button_back)
    db.close()
    return keyboard


def get_keyboard_inline_appointment_delete():
    keyboard = types.InlineKeyboardMarkup()
    button_del = types.InlineKeyboardButton(text='Отмена записи', callback_data='del')
    keyboard.add(button_del)
    return keyboard


def get_keyboard_inline_appointment_delete_sure():
    keyboard = types.InlineKeyboardMarkup()
    button_yes_in = types.InlineKeyboardButton(text='Да', callback_data='sure_yes')
    button_no_in = types.InlineKeyboardButton(text='Нет', callback_data='sure_no')
    keyboard.add(button_no_in, button_yes_in)
    return keyboard
