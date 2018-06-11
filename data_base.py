# coding=utf-8
import psycopg2
import telebot
import config


class DataBase:
    def __init__(self):
        self.connection = psycopg2.connect(dbname='d41946bputpkfi', user='tdbinirjdxxdzf',
                                           password='1ad38e225b4cc064ebcdfa76d4934fbe116bca6cec6bb5e5562d148e94661d8c',
                                           host='ec2-54-75-239-237.eu-west-1.compute.amazonaws.com')

        self.cursor = self.connection.cursor()

    def get_keyboard_pet(self):
        keyboard_pet = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        with self.connection:
            self.cursor.execute("SELECT nametypepet FROM ttypepet")
            for n in list(self.cursor):
                keyboard_pet.add(str(n[0]))
            return keyboard_pet

    def get_keyboard_type(self):
        keyboard_type = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        with self.connection:
            self.cursor.execute("SELECT nameappointmenttype FROM tappointmenttype")
            for n in list(self.cursor):
                keyboard_type.add(str(n[0]))
            return keyboard_type

    def check_user(self, id):
        with self.connection:
            self.cursor.execute("SELECT COUNT(*) FROM dialog_bot WHERE id_user = %s", [id])
            # cursor.execute("SELECT COUNT(*) FROM towner WHERE id_chat_owner = %s AND ownerfirstname IS NOT NULL", [id])
            return bool(self.cursor.fetchone()[0])

    def check_pet_type(self, msg):
        with self.connection:
            self.cursor.execute("SELECT COUNT(*) FROM ttypepet WHERE nametypepet = %s", [msg.text])
            return bool(self.cursor.fetchone()[0])

    def check_pet_name(self, msg):
        with self.connection:
            self.cursor.execute("SELECT COUNT(*) FROM tpet WHERE petname = %s AND id_owner = %s",
                                [msg.text, self.get_owner_id(msg)])
            return not (bool(self.cursor.fetchone()[0]))

    def check_pet_gender(self, msg):
        return (msg.text == u'Мальчик') or (msg.text == u'Девочка')


    def check_appointment_type(self, msg):
        with self.connection:
            self.cursor.execute("SELECT COUNT(*) FROM tappointmenttype WHERE nameappointmenttype= %s", [msg.text])
            return bool(self.cursor.fetchone()[0])

    def check_pet(self, msg):
        with self.connection:
            self.cursor.execute("SELECT * FROM tpet WHERE id_owner = %s", [self.get_owner_id(msg)])
            return bool(self.cursor.rowcount)

    def check_pet_owner(self, msg):
        with self.connection:
            self.cursor.execute("SELECT COUNT(*) FROM tpet WHERE petname = %s AND id_owner = %s",
                                [msg.text, self.get_owner_id(msg)])
            return bool(self.cursor.fetchone()[0])

    def write_data_owner(self, msg):
        with self.connection:
            status = self.get_current_status(msg.chat.id)
            if status == config.states_user.get('owner_phone'):
                self.cursor.execute("INSERT INTO towner (id_chat_owner, ownernumber) VALUES (%s, %s)",
                                    [msg.chat.id, msg.contact.phone_number])
            if status == config.states_user.get('owner_name'):
                self.cursor.execute("UPDATE towner SET ownername = %s WHERE id_chat_owner = %s",
                                    [msg.text, msg.chat.id])
            if status == config.states_user.get('owner_first_name'):
                self.cursor.execute("UPDATE towner SET ownerfirstname = %s WHERE id_chat_owner = %s",
                                    [msg.text, msg.chat.id])
            self.connection.commit()

    def write_data_appointment(self, msg):
        with self.connection:
            status = self.get_current_status(msg.chat.id)
            if status == config.states_user.get('appointment_pet'):
                self.cursor.execute("SELECT id_statustype FROM tstatustype WHERE namestatustype = %s", ["Идет запись"])
                id_status_type = self.cursor.fetchone()[0]
                self.cursor.execute("SELECT id_pet FROM tpet WHERE petname = %s AND id_owner = %s",
                                    [msg.text, self.get_owner_id(msg)])
                id_pet = self.cursor.fetchone()[0]
                self.cursor.execute("INSERT INTO tappointment (id_pet, id_statustype) VALUES(%s, %s)",
                                    [id_pet, id_status_type])

            if self.get_current_status(msg.chat.id) == config.states_user.get('appointment_type'):
                self.cursor.execute("SELECT id_appointmenttype FROM tappointmenttype WHERE nameappointmenttype = %s",
                                    [msg.text])
                id_appointment_type = self.cursor.fetchone()[0]
                self.cursor.execute("SELECT id_statustype FROM tstatustype WHERE namestatustype = %s", ["Идет запись"])
                id_status_type = self.cursor.fetchone()[0]
                self.cursor.execute(
                    "UPDATE tappointment SET id_appointmenttype = %s WHERE id_statustype = %s AND id_pet IN "
                    "(SELECT id_pet FROM tpet WHERE id_owner = %s)",
                    [id_appointment_type, id_status_type, self.get_owner_id(msg)])

            if self.get_current_status(msg.chat.id) == config.states_user.get('appointment_done'):
                self.cursor.execute("SELECT id_statustype FROM tstatustype WHERE namestatustype = %s",
                                    ["Неподтвержденная"])
                id_status_type_new = self.cursor.fetchone()[0]
                self.cursor.execute("SELECT id_statustype FROM tstatustype WHERE namestatustype = %s", ["Идет запись"])
                id_status_type_old = self.cursor.fetchone()[0]
                self.cursor.execute("UPDATE tappointment SET id_statustype = %s WHERE id_statustype = %s AND id_pet IN "
                                    "(SELECT id_pet FROM tpet WHERE id_owner = %s)",
                                    [id_status_type_new, id_status_type_old, self.get_owner_id(msg)])
            self.connection.commit()

    def write_data_pet(self, msg):
        with self.connection:
            status = self.get_current_status(msg.chat.id)
            if status == config.states_user.get('pet_type'):
                self.cursor.execute("SELECT id_typepet FROM ttypepet WHERE nametypepet = %s", [msg.text])
                id_type_pet = self.cursor.fetchone()[0]
                self.cursor.execute("INSERT INTO tpet (id_typepet, id_owner) VALUES(%s, %s)",
                                    [id_type_pet, self.get_owner_id(msg)])

            if status == config.states_user.get('pet_name'):
                self.cursor.execute("SELECT id_pet FROM tpet WHERE id_owner = %s AND petname IS NULL",
                                    [self.get_owner_id(msg)])
                id_pet = self.cursor.fetchone()[0]
                self.cursor.execute("UPDATE tpet SET petname = %s WHERE id_pet = %s", [msg.text, id_pet])

            if status == config.states_user.get('pet_gender'):
                self.cursor.execute("SELECT id_pet FROM tpet WHERE id_owner = %s AND gender IS NULL",
                                    [self.get_owner_id(msg)])
                id_pet = self.cursor.fetchone()[0]
                gender = (msg.text == u'Мальчик')
                self.cursor.execute("UPDATE tpet SET gender = %s WHERE id_pet = %s", [gender, id_pet])

            self.connection.commit()

    def get_current_status(self, id):
        with self.connection:
            if self.check_user(id):
                self.cursor.execute("SELECT id_dialog_bot_type FROM dialog_bot WHERE id_user = %s", [id])
                return self.cursor.fetchone()[0]
            else:
                return 0

    def write_dialog_status(self, id, status):
        with self.connection:
            self.cursor.execute("SELECT COUNT(*) FROM dialog_bot WHERE id_user = %s", [id])
            if bool(self.cursor.fetchone()[0]):
                self.cursor.execute("UPDATE dialog_bot SET id_dialog_bot_type = %s WHERE id_user = %s", [status, id])
            else:
                self.cursor.execute("INSERT INTO dialog_bot (id_user, id_dialog_bot_type) VALUES (%s, %s)",
                                    [id, status])

            self.connection.commit()

    def check_appointments(self, msg):
        with self.connection:
            self.cursor.execute("SELECT id_statustype FROM tstatustype WHERE namestatustype = %s", ["Завершенная"])
            id_status_type = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT * FROM tappointment WHERE id_statustype <> %s AND id_pet IN "
                                "(SELECT id_pet FROM tpet WHERE id_owner = %s)",
                                [id_status_type, self.get_owner_id(msg)])
            return bool(self.cursor.rowcount)

    def get_appointments(self, msg):
        with self.connection:
            if self.check_appointments(msg):
                self.cursor.execute("SELECT id_statustype FROM tstatustype WHERE namestatustype = %s", ["Завершенная"])
                id_status_type = self.cursor.fetchone()[0]
                self.cursor.execute("SELECT * FROM tappointment WHERE id_statustype <> %s AND id_pet IN "
                                    "(SELECT id_pet FROM tpet WHERE id_owner = %s)",
                                    [id_status_type, self.get_owner_id(msg)])
                return list(self.cursor.fetchall())
            else:
                return None

    def get_appointment_type(self, id):
        with self.connection:
            self.cursor.execute("SELECT nameappointmenttype FROM tappointmenttype WHERE id_appointmenttype = %s", [id])
            return str(self.cursor.fetchone()[0])

    def get_status_type(self, id):
        with self.connection:
            self.cursor.execute("SELECT namestatustype FROM tstatustype WHERE id_statustype = %s", [id])
            return str(self.cursor.fetchone()[0])

    def get_typepet(self, id):
        with self.connection:
            self.cursor.execute("SELECT nametypepet FROM ttypepet WHERE id_typepet = %s", [id])
            return str(self.cursor.fetchone()[0])

    def get_pet_info(self, id):
        with self.connection:
            self.cursor.execute("SELECT petname,id_typepet FROM tpet WHERE id_pet = %s", [id])
            for n in list(self.cursor):
                string = str(n[0] + '\n' + self.get_typepet(n[1]))
            return string

    def delete_appointment(self, id):
        with self.connection:
            self.cursor.execute("DELETE FROM tappointment WHERE id_appointment = %s", [id])
            self.connection.commit()

    def make_keyboard_pets(self, msg):
        with self.connection:
            keyboard_pet_owner = telebot.types.ReplyKeyboardMarkup(row_width=2)
            self.cursor.execute("SELECT petname FROM tpet WHERE id_owner = %s", [self.get_owner_id(msg)])
            for n in list(self.cursor):
                keyboard_pet_owner.add(str(str(n[0])))
            keyboard_pet_owner.add('Добавить нового питомца')
            return keyboard_pet_owner

    def delete_owner_start(self, msg):
        with self.connection:
            self.cursor.execute("DELETE FROM towner WHERE id_chat_owner = %s", [msg.chat.id])
            self.connection.commit()

    def delete_appointment_start(self, msg):
        with self.connection:
            self.cursor.execute("DELETE FROM tappointment WHERE id_appointmenttype is NULL AND id_pet IN "
                                "(SELECT id_pet FROM tpet WHERE id_owner = %s)", [self.get_owner_id(msg)])
            self.connection.commit()

    def delete_pet_start(self, msg):
        with self.connection:
            self.cursor.execute("DELETE FROM tpet WHERE (((gender IS NULL) OR (petname IS NULL)) AND id_owner = %s)",
                                [self.get_owner_id(msg)])
            self.connection.commit()

    def get_owner_id(self, msg):
        with self.connection:
            self.cursor.execute("SELECT id_owner FROM towner WHERE id_chat_owner = %s", [msg.chat.id])
            return self.cursor.fetchone()[0]

    def close(self):
        self.connection.close()
