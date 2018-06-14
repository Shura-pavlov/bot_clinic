# -*- coding: utf-8 -*-
from telebot import types
from data_base import DataBase
from config import button_texts

# keyboards
# ------------------------------
button_back = types.KeyboardButton(text=button_texts.get(0))


def get_keyboard_telephone():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button_telephone = types.KeyboardButton(text=button_texts.get(1), request_contact=True)
    keyboard.add(button_telephone)
    return keyboard


def get_keyboard_menu():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button_add = types.KeyboardButton(text=button_texts.get(2))
    button_see = types.KeyboardButton(text=button_texts.get(3))
    button_setting = types.KeyboardButton(text=button_texts.get(4))
    keyboard.add(button_add, button_see,
                 button_setting)
    return keyboard


def get_keyboard_menu_edit():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button_pet = types.KeyboardButton(text=button_texts.get(5))
    button_owner = types.KeyboardButton(text=button_texts.get(6))
    keyboard.add(button_pet, button_owner,
                 button_back)
    return keyboard


def get_keyboard_edit_pet():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button_breed = types.KeyboardButton(text=button_texts.get(7))
    button_weight = types.KeyboardButton(text=button_texts.get(8))
    button_info = types.KeyboardButton(text=button_texts.get(9))
    keyboard.add(button_breed, button_weight,
                 button_info, button_back)
    return keyboard


def get_keyboard_edit_owner():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button_name = types.KeyboardButton(text=button_texts.get(10))
    button_first_name = types.KeyboardButton(text=button_texts.get(11))
    button_second_name = types.KeyboardButton(text=button_texts.get(12))
    button_address = types.KeyboardButton(text=button_texts.get(13))
    button_email = types.KeyboardButton(text=button_texts.get(14))
    keyboard.add(button_name, button_first_name,
                 button_second_name, button_address,
                 button_email, button_back)
    return keyboard


def get_keyboard_gender():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button_boy = types.KeyboardButton(text=button_texts.get(15))
    button_girl = types.KeyboardButton(text=button_texts.get(16))
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


def get_keyboard_pets(msg):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    db = DataBase()
    for n in db.get_pets(msg):
        keyboard.add(str(str(n)))
    keyboard.add(button_texts.get(20))
    db.close()
    return keyboard


def get_keyboard_inline_appointment_delete():
    keyboard = types.InlineKeyboardMarkup()
    button_del = types.InlineKeyboardButton(text=button_texts.get(17), callback_data='del')
    keyboard.add(button_del)
    return keyboard


def get_keyboard_inline_appointment_delete_sure():
    keyboard = types.InlineKeyboardMarkup()
    button_yes_in = types.InlineKeyboardButton(text=button_texts.get(18), callback_data='sure_yes')
    button_no_in = types.InlineKeyboardButton(text=button_texts.get(19), callback_data='sure_no')
    keyboard.add(button_no_in, button_yes_in)
    return keyboard
