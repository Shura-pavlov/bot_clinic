# -*- coding: utf-8 -*-

import config
import keyboards
from data_base import DataBase
import telebot
import re
import datetime

bot = telebot.TeleBot(config.token)

# TODO: вынести отдельно диалоги на кнопках и ответах
# TODO: добавить переходы по идалогам назад и в главное меню в любом месте


def get_error_message(message):
    bot.send_message(message.chat.id, 'Не понимаю, но очень стараюсь. Пожалуйста, попробуйте заново')


# cleaning db
@bot.message_handler(commands=["start"])
def start_check(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'Вас приветствует клиника "Mascotas"!')
    db_worker = DataBase()
    if db_worker.check_user(message.chat.id):
        number = db_worker.get_current_status(message.chat.id)
        if number == 0:
            menu_start(message)
        else:
            if ((number == config.states_user.get('owner_name')) or
                    (number == config.states_user.get('owner_first_name'))):
                db_worker.delete_owner_start(message)
                add_owner_phone(message)

            if ((number == config.states_user.get('appointment_type')) or
                    (number == config.states_user.get('appointment_date')) or
                    (number == config.states_user.get('appointment_time'))):
                db_worker.delete_appointment_start(message)

            if ((number == config.states_user.get('pet_type')) or
                    (number == config.states_user.get('pet_name')) or
                    (number == config.states_user.get('pet_gender'))):
                db_worker.delete_pet_start(message)

            db_worker.write_dialog_status(message.chat.id, config.states_user.get('sleep'))
            db_worker.close()
            menu_start(message)
    else:
        db_worker.close()
        add_owner_phone(message)


# first-time-user
# ------------------------------
def add_owner_phone(message):
    bot.send_message(message.chat.id, 'Вижу вас впервые! Пожалуйста, сообщите ваш телефон для продолжения работы',
                     reply_markup=keyboards.get_keyboard_telephone())
    db_worker = DataBase()
    db_worker.write_dialog_status(message.chat.id, config.states_user.get('owner_phone'))
    bot.register_next_step_handler(message, add_owner_name)
    db_worker.close()


def add_owner_name(message):
    db_worker = DataBase()
    db_worker.write_data_owner(message)
    bot.send_message(message.chat.id, 'Как ваше имя?')
    db_worker.write_dialog_status(message.chat.id, config.states_user.get('owner_name'))
    db_worker.close()
    bot.register_next_step_handler(message, add_owner_first_name)


def add_owner_first_name(message):
    db_worker = DataBase()
    db_worker.write_data_owner(message)
    bot.send_message(message.chat.id, 'А фамилия?')
    db_worker.write_dialog_status(message.chat.id, config.states_user.get('owner_first_name'))
    db_worker.close()
    bot.register_next_step_handler(message, add_owner_second_name)


def add_owner_second_name(message):
    db_worker = DataBase()
    db_worker.write_data_owner(message)
    bot.send_message(message.chat.id, 'Вы успешно добавлены!')
    db_worker.write_dialog_status(message.chat.id, config.states_user.get('owner_done'))
    db_worker.write_dialog_status(message.chat.id, config.states_user.get('sleep'))
    db_worker.close()
    menu_start(message)


# ------------------------------


def menu_start(message):
    bot.send_message(message.chat.id, 'Что вы хотите сделать?', reply_markup=keyboards.get_keyboard_menu())
    bot.register_next_step_handler(message, answer_menu_start)


def answer_menu_start(msg):
    if msg.text == u'Записаться на прием':
        appointment_new(msg)
    elif msg.text == u'Просмотр записи':
        appointment_see(msg)
        menu_start(msg)
    elif msg.text == u'Настройка':
        menu_edit(msg)
    else:
        get_error_message(msg)
        menu_start(msg)


# edit
# ------------------------------
def menu_edit(msg):
    bot.send_message(msg.chat.id, 'Что будем редактировать?', reply_markup=keyboards.get_keyboard_menu_edit())
    bot.register_next_step_handler(msg, answer_menu_edit)


def answer_menu_edit(msg):
    if msg.text == u'Редактор Питомцев':
        menu_edit_choose_pet(msg)
    elif msg.text == u'Редактор Пользователя':
        menu_edit_owner(msg)
    elif msg.text == u'Назад':
        menu_start(msg)
    else:
        get_error_message(msg)
        menu_edit(msg)


def menu_edit_choose_pet(message):
    db_worker = DataBase()
    if db_worker.check_pet(message):
        keyboard_pet_owner = db_worker.make_keyboard_pets(message)
        bot.send_message(message.chat.id, 'Выберите питомца', reply_markup=keyboard_pet_owner)
        bot.register_next_step_handler(message, menu_edit_pet_status)
    else:
        bot.send_message(message.chat.id, 'У вас нет питомцев!')
        menu_edit(message)


def menu_edit_pet_status(msg):
    db_worker = DataBase()
    if db_worker.check_pet_owner(msg):
        db_worker.set_status_type_pet(msg)
        menu_edit_pet(msg)
    else:
        get_error_message(msg)
        menu_edit(msg)


def menu_edit_pet(msg):
    bot.send_message(msg.chat.id, 'Выберите редактируемую опцию', reply_markup=keyboards.get_keyboard_edit_pet())
    bot.register_next_step_handler(msg, answer_menu_edit_pet)


def answer_menu_edit_pet(msg):
    if msg.text == u'Порода':
        edit_breed(msg)
    elif msg.text == u'Вес':
        edit_weight(msg)
    elif msg.text == u'О питомце':
        edit_info(msg)
    elif msg.text == u'Назад':
        db_worker = DataBase()
        db_worker.set_sleep_status_pet(msg)
        menu_edit(msg)
    else:
        get_error_message(msg)
        menu_edit_pet(msg)


def edit_breed(msg):
    bot.send_message(msg.chat.id, 'Введите породу вашего питомца')
    db_worker = DataBase()
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('edit_breed'))
    db_worker.close()
    bot.register_next_step_handler(msg, answer_edit_breed)


def answer_edit_breed(msg):
    db_worker = DataBase()
    db_worker.write_data_pet(msg)
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('sleep'))
    db_worker.close()
    bot.send_message(msg.chat.id, 'Информация записана')
    menu_edit_pet(msg)


def edit_weight(msg):
    bot.send_message(msg.chat.id, 'Введите вес вашего питомца')
    db_worker = DataBase()
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('edit_weight'))
    db_worker.close()
    bot.register_next_step_handler(msg, answer_edit_weight)


def answer_edit_weight(msg):
    db_worker = DataBase()
    db_worker.write_data_pet(msg)
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('sleep'))
    db_worker.close()
    bot.send_message(msg.chat.id, 'Информация записана')
    menu_edit_pet(msg)


def edit_info(msg):
    bot.send_message(msg.chat.id, 'Введите информацию вашего питомца')
    db_worker = DataBase()
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('edit_info'))
    db_worker.close()
    bot.register_next_step_handler(msg, answer_edit_info)


def answer_edit_info(msg):
    db_worker = DataBase()
    db_worker.write_data_pet(msg)
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('sleep'))
    db_worker.close()
    bot.send_message(msg.chat.id, 'Информация записана')
    menu_edit_pet(msg)


def menu_edit_owner(msg):
    bot.send_message(msg.chat.id, 'Выберите редактируемую опцию', reply_markup=keyboards.get_keyboard_edit_owner())
    bot.register_next_step_handler(msg, answer_menu_edit_owner)


def answer_menu_edit_owner(msg):
    if msg.text == u'Имя':
        edit_name(msg)
    elif msg.text == u'Фамилия':
        edit_first_name(msg)
    elif msg.text == u'Отчество':
        edit_second_name(msg)
    elif msg.text == u'Адрес проживания':
        edit_address(msg)
    elif msg.text == u'Почта':
        edit_email(msg)
    elif msg.text == u'Назад':
        menu_edit(msg)
    else:
        get_error_message(msg)
        menu_edit_owner(msg)


def edit_name(msg):
    bot.send_message(msg.chat.id, 'Введите новое имя')
    db_worker = DataBase()
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('edit_name'))
    db_worker.close()
    bot.register_next_step_handler(msg, answer_edit_name)


def answer_edit_name(msg):
    db_worker = DataBase()
    db_worker.write_data_owner(msg)
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('sleep'))
    db_worker.close()
    bot.send_message(msg.chat.id, 'Информация записана')
    menu_edit_owner(msg)


def edit_first_name(msg):
    bot.send_message(msg.chat.id, 'Введите новую фамилию')
    db_worker = DataBase()
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('edit_first_name'))
    db_worker.close()
    bot.register_next_step_handler(msg, answer_edit_first_name)


def answer_edit_first_name(msg):
    db_worker = DataBase()
    db_worker.write_data_owner(msg)
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('sleep'))
    db_worker.close()
    bot.send_message(msg.chat.id, 'Информация записана')
    menu_edit_owner(msg)


def edit_second_name(msg):
    bot.send_message(msg.chat.id, 'Введите новое отчество')
    db_worker = DataBase()
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('edit_second_name'))
    db_worker.close()
    bot.register_next_step_handler(msg, answer_edit_second_name)


def answer_edit_second_name(msg):
    db_worker = DataBase()
    db_worker.write_data_owner(msg)
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('sleep'))
    db_worker.close()
    bot.send_message(msg.chat.id, 'Информация записана')
    menu_edit_owner(msg)


def edit_address(msg):
    bot.send_message(msg.chat.id, 'Введите адрес')
    db_worker = DataBase()
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('edit_address'))
    db_worker.close()
    bot.register_next_step_handler(msg, answer_edit_address)


def answer_edit_address(msg):
    db_worker = DataBase()
    db_worker.write_data_owner(msg)
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('sleep'))
    db_worker.close()
    bot.send_message(msg.chat.id, 'Информация записана')
    menu_edit_owner(msg)


def edit_email(msg):
    bot.send_message(msg.chat.id, 'Введите свою электронную почту')
    db_worker = DataBase()
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('edit_email'))
    db_worker.close()
    bot.register_next_step_handler(msg, answer_edit_email)


def answer_edit_email(msg):
    db_worker = DataBase()
    db_worker.write_data_owner(msg)
    db_worker.write_dialog_status(msg.chat.id, config.states_user.get('sleep'))
    db_worker.close()
    bot.send_message(msg.chat.id, 'Информация записана')
    menu_edit_owner(msg)


# ------------------------------

# appointment
# ------------------------------
def appointment_new(message):
    bot.send_message(message.chat.id, 'Следуйте указаниям бота')
    appointment_pet(message)


def appointment_pet(message):
    db_worker = DataBase()
    if db_worker.check_pet(message):
        keyboard_pet_owner = db_worker.make_keyboard_pets(message)
        bot.send_message(message.chat.id, 'Выберите своего питомца',
                         reply_markup=keyboard_pet_owner)
        bot.register_next_step_handler(message, answer_appointment_pet)
    else:
        bot.send_message(message.chat.id, 'Не нахожу у тебя питомцев. Непорядок, надо добавить')
        add_new_pet_type(message)
    db_worker.close()


def answer_appointment_pet(msg):
    db_worker = DataBase()
    if msg.text == u'Добавить нового питомца':
        add_new_pet_type(msg)
    else:
        if db_worker.check_pet_owner(msg):
            db_worker.write_dialog_status(msg.chat.id, config.states_user.get('appointment_pet'))
            appointment_type(msg)
        else:
            get_error_message(msg)
            appointment_pet(msg)
    db_worker.close()


def add_new_pet_type(message):
    db_worker = DataBase()
    bot.send_message(message.chat.id, 'Укажите вид питомца', reply_markup=db_worker.get_keyboard_pet())
    db_worker.write_dialog_status(message.chat.id, config.states_user.get('pet_type'))
    db_worker.close()


@bot.message_handler(
    func=lambda message: db_worker1.get_current_status(message.chat.id) == config.states_user.get('pet_type'))
def add_new_pet_name(message):
    db_worker = DataBase()
    if db_worker.check_pet_type(message):
        db_worker.write_data_pet(message)
        bot.send_message(message.chat.id, 'Напишите имя питомца (помните, оно должно быть уникальным среди ваших '
                                          'питомцев)')
        db_worker.write_dialog_status(message.chat.id, config.states_user.get('pet_name'))
    else:
        get_error_message(message)
    db_worker.close()


@bot.message_handler(
    func=lambda message: db_worker1.get_current_status(message.chat.id) == config.states_user.get('pet_name'))
def add_new_pet_gender(message):
    db_worker = DataBase()
    if db_worker.check_pet_name(message):
        db_worker.write_data_pet(message)
        bot.send_message(message.chat.id, 'Укажите пол питомца', reply_markup=keyboards.get_keyboard_gender())
        db_worker.write_dialog_status(message.chat.id, config.states_user.get('pet_gender'))
    else:
        get_error_message(message)
    db_worker.close()


@bot.message_handler(
    func=lambda message: db_worker1.get_current_status(message.chat.id) == config.states_user.get('pet_gender'))
def add_new_pet_done(message):
    db_worker = DataBase()
    if db_worker.check_pet_gender(message):
        db_worker.write_data_pet(message)
        bot.send_message(message.chat.id, 'Питомец успешно добавлен!')
        db_worker.write_dialog_status(message.chat.id, config.states_user.get('appointment_pet'))
        appointment_pet(message)
    else:
        get_error_message(message)
    db_worker.close()


def appointment_type(message):
    db_worker = DataBase()
    db_worker.write_data_appointment(message)
    bot.send_message(message.chat.id, 'Выберите тип приема', reply_markup=db_worker.get_keyboard_type())
    db_worker.write_dialog_status(message.chat.id, config.states_user.get('appointment_type'))
    db_worker.close()


@bot.message_handler(
    func=lambda message: db_worker1.get_current_status(message.chat.id) == config.states_user.get('appointment_type'))
def appointment_date(message):
    db_worker = DataBase()
    if db_worker.check_appointment_type(message):
        db_worker.write_data_appointment(message)
        bot.send_message(message.chat.id, 'Выберите дату приема', reply_markup=keyboards.get_keyboard_date())
        db_worker.write_dialog_status(message.chat.id, config.states_user.get('appointment_date'))
    else:
        get_error_message(message)
    db_worker.close()


@bot.message_handler(
    func=lambda message: db_worker1.get_current_status(message.chat.id) == config.states_user.get('appointment_date'))
def appointment_time(message):
    db_worker = DataBase()
    if db_worker.check_appointment_date(message):
        db_worker.write_data_appointment(message)
        res = re.findall(r'\d+', message.text)
        day = datetime.date(int(res.pop()), int(res.pop()), int(res.pop()))
        bot.send_message(message.chat.id, 'Выберите время приема', reply_markup=keyboards.get_keyboard_time(day))
        db_worker.write_dialog_status(message.chat.id, config.states_user.get('appointment_time'))
    else:
        get_error_message(message)
    db_worker.close()


@bot.message_handler(
    func=lambda message: db_worker1.get_current_status(message.chat.id) == config.states_user.get('appointment_time'))
def appointment_done(message):
    db_worker = DataBase()
    if message.text == u'Назад':
        bot.send_message(message.chat.id, 'Выберите дату приема', reply_markup=keyboards.get_keyboard_date())
        db_worker.write_dialog_status(message.chat.id, config.states_user.get('appointment_date'))
    elif db_worker.check_appointment_time(message):
        db_worker.write_data_appointment(message)
        bot.send_message(message.chat.id, 'Запись успешно добавлена!')
        db_worker.write_dialog_status(message.chat.id, config.states_user.get('appointment_done'))
        db_worker.write_data_appointment(message)
        db_worker.write_dialog_status(message.chat.id, config.states_user.get('sleep'))
        menu_start(message)
    else:
        get_error_message(message)
    db_worker.close()


# ------------------------------
def appointment_see(message):
    db_worker = DataBase()
    appointment_list = db_worker.get_appointments(message)
    if appointment_list:
        message_list = []
        for n in appointment_list:
            message_list.append(get_appointment_info(n))
        for n in message_list:
            bot.send_message(message.chat.id, n, reply_markup=keyboards.get_keyboard_inline_appointment_delete())
    else:
        bot.send_message(message.chat.id, 'Не найдено записей!')
    db_worker.close()


def get_appointment_info(array):
    db_worker = DataBase()
    string = ''
    string += 'Запись   # ' + str(array[0]) + '\n'
    string += db_worker.get_pet_info(str(array[1])) + '\n'
    string += 'Тип приема:  ' + db_worker.get_appointment_type(array[3]) + '\n'
    string += 'Статус:  ' + db_worker.get_status_type(array[4]) + '\n'
    string += 'Дата:   ' + array[7].strftime("%d / %m / %Y, %A") + '\n'
    string += 'Время:   ' + array[8].strftime("%H:%M")
    db_worker.close()
    return string


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'del':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text,
                              reply_markup=keyboards.get_keyboard_inline_appointment_delete_sure())
    elif call.data == 'sure_yes':
        search_appointment(call.message.text)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Запись отменена")
    elif call.data == 'sure_no':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text,
                              reply_markup=keyboards.get_keyboard_inline_appointment_delete())


def search_appointment(msg):
    db_worker = DataBase()
    res = re.search(r'\d+', msg)
    db_worker.delete_appointment(res.group(0))
    db_worker.close()


if __name__ == '__main__':
    db_worker1 = DataBase()
    # threading.Thread(target=bot.polling(none_stop=True)).start()
    bot.polling(none_stop=True)
    db_worker1.close()
