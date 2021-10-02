# -*- coding: utf-8 -*-
# Файл для работы с бд

'''
 Для heroku придётся использовать базу данных,
 т.к. данные не сохраняются
'''

import psycopg2
import dj_database_url
import os
from datetime import datetime



# Для представления ссылки на базу в её данные (логин, пароль и т.д.) postgres://USER:PASSWORD@HOST:PORT/NAME

class PSQLighter:

    def __init__(self):
        try:

            # Строка для heroku
            database = os.environ['pgsql_db']

            self.connection = psycopg2.connect(database)
            self.cursor = self.connection.cursor()
            self.connection.set_client_encoding('UTF8')
            self.id_feedback = None
            print("connection success")
        except Exception as e:
            print("Ошибка __init__: %s" % str(e))

    # Создание нового пользователя
    def create_user(self, user):
        try:
            with self.connection:
                self.cursor.execute('''INSERT INTO users(user_id, user_name, first_name, last_name) VALUES (%s, \'%s\', \'%s\', \'%s\') RETURNING id;''' % (
                    user.id, user.username, user.first_name, user.last_name))
                id_of_new_row = self.cursor.fetchone()[0]
                self.connection.commit
            return user.id
        except Exception as e:
            print("Ошибка: %s" % str(e))

    # Проверка пользователя на существование.
    def check_exist_client(self, user):
        cursor = self.connection.cursor()
        cursor.execute('''SELECT count(*) FROM users where user_id = %s;''' % (user.id))
        result = cursor.fetchone()
        res = cursor.fetchone()
        count = result[0]
        if count > 0:
            self.user_id = user.id
        else:
            self.user_id = self.create_user(user)

    # Создание ИД отзыва.
    def create_feedback_id(self):
        try:
            with self.connection:
                self.cursor.execute('''insert into food_list default values RETURNING id''' )
                id_of_new_row = self.cursor.fetchone()[0]
                self.connection.commit
                self.id_feedback = id_of_new_row
            return id_of_new_row
        except Exception as e:
            print("Ошибка create_feedback_id: %s" % str(e))

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()

    # Записываем описание.
    def set_descr(self, message):
        try:
            if self.user_id is None:
                self.check_exist_client(self, message.user)
            if self.id_feedback is None:
                self.create_feedback_id()
            with self.connection:
                 self.cursor.execute('''UPDATE food_list SET descr = \'%s\' WHERE id = %s;''' % (
                     message.text, self.id_feedback))
                 self.connection.commit
        except Exception as e:
            print("Ошибка set_descr: %s" % str(e))

    # Записываем оценку
    def set_score(self, text):
        try:
            score = 0
            if text == 'shit':
                score = -1
            elif text == 'good':
                score = 1
            with self.connection:
                 self.cursor.execute('''UPDATE food_list SET score = \'%s\' WHERE id = %s;''' % (
                     score, self.id_feedback))
                 self.connection.commit
        except Exception as e:
            print("Ошибка set_score: %s" % str(e))

    # Получаем ИД категории
    def get_category_id(self, message):
        try:
            cursor = self.connection.cursor()
            cursor.execute('''select id from categories where name = \'%s\';''' % (message.text))
            result = cursor.fetchone()
            res = cursor.fetchone()
            if result is None :
                self.cat_id = self.create_category_id(message)
            else:
                self.cat_id = result[0]
            return self.cat_id
        except Exception as e:
            print("Ошибка get_cat_id: %s" % str(e))

    # Создание ИД категории.
    def create_category_id(self, message):
        try:
            with self.connection:
                self.cursor.execute('''insert into categories(name) values(\'%s\') RETURNING id''' %(message.text))
                id_of_new_row = self.cursor.fetchone()[0]
                self.connection.commit
                self.cat_id = id_of_new_row
                return self.cat_id
        except Exception as e:
            print("Ошибка create_category_id: %s" % str(e))

    # Установка категории
    def set_category(self, message):
        try:
            if self.user_id is None:
                self.check_exist_client(self, message.user)
            if self.id_feedback is None:
                self.create_feedback_id()
            cat_id = self.get_category_id(message)
            text = '#' + message.text
            with self.connection:
                 self.cursor.execute('''UPDATE food_list SET cat_id = %s WHERE id = %s;''' % (
                     cat_id, self.id_feedback))
                 self.connection.commit
        except Exception as e:
            print("Ошибка set_category: %s" % str(e))


    def set_client_phone(self, contact, username):
        """
        Добавляем телефон клиента
        :param contact: Отправленный клиентом контакт
        :param username: юзернейм клиента
        """
        with self.connection:
            if self.check_exist_client(contact.user_id):
                self.cursor.execute('''UPDATE clients SET phone_number = \'%s\' WHERE Id = %s;''' % (
                contact.phone_number, contact.user_id))
            else:
                self.cursor.execute(
                    '''INSERT INTO clients(Id, username, first_name, phone_number) VALUES(%s, \'%s\', \'%s\', \'%s\');''' % (
                    contact.user_id, username, contact.first_name, contact.phone_number))
        return None

    def set_order(self, Id, IdClient, Item, Vol, OrderTime):
        """
        Добавляем заказ. Из параметров Item, Vol, OrderTime передаем только один.
        :param Id: Id заказа.
        :param IdClient: Id пользователя.
        :param Item: Что покупаем.
        :param Vol: юзернейм клиента.
        :param OrderTime: юзернейм клиента.
        :return: ИД добавленной записи.
        """
        try:
            with self.connection:
                cursor = self.connection.cursor()
                # Добавляем что.
                if (IdClient is not None):
                    # Вставляем заказ
                    if (Item != "") and (Id is None):
                        cursor.execute('''INSERT INTO Orders(IdClient, Item) VALUES (%s, \'%s\') RETURNING id;''' % (
                        IdClient, Item))
                        id_of_new_row = cursor.fetchone()[0]
                        self.connection.commit
                        return id_of_new_row
                    # Добавляем объем заказа
                    if (Vol is not None) and (Id is not None):
                        cursor.execute('''UPDATE Orders SET Vol = \'%s\' WHERE Id = %s ;''' % (Vol, Id))
                        self.connection.commit
                        return Id
                    # Добавляем время заказа
                    if (OrderTime is not None) and (Id is not None):
                        dt = datetime.now()
                        cursor.execute(
                            '''UPDATE Orders SET OrderTime = \'%s\', DateCreate = \'%s\' WHERE Id = %s;''' % (
                            OrderTime, dt, Id))
                        self.connection.commit
                        return Id
                else:
                    return None
        except Exception as e:
            print("Ошибка set_order: %s" % str(e))

    def get_order_string(self, id, tobar=0):
        try:
            with self.connection:
                cursor = self.connection.cursor()
                # Текст заказа для клиrента
                if tobar == 0:
                    cursor.execute('''SELECT Item, Vol, OrderTime   FROM orders where Id = %s;''' % (id))
                    res = cursor.fetchone()
                    if res[1] is None:
                        r1 = ''
                    else:
                        r1 = res[1]
                    return res[0] + ', ' + r1 + ', ' + res[2]

                # Текст заказа для баристы
                elif tobar == 1:
                    res = cursor.execute(
                        '''SELECT Item, Vol, OrderTime, Clients.first_name, orders.Id FROM Orders LEFT JOIN Clients ON orders.IdClient = Clients.Id where Orders.Id  = %s;''' % (
                            id))
                    res = cursor.fetchone()
                    if res[1] is None:
                        r1 = ''
                    else:
                        r1 = res[1]

                    if res is not None:
                        return '# ' + str(res[4]) + ' Name: ' + res[3] + ', ' + res[0] + ', ' + r1 + ', ' + res[2]
                else:
                    return None
        except Exception as e:
            print("Ошибка get_order_string : %s" % str(e))

    def del_order(self, id):
        """
        Удаляем заказ.
        :param id: Id заказа.
        """
        try:
            with self.connection:
                if (id is not None):
                    self.cursor.execute('''DELETE FROM Orders where Id = %s;''' % (id))
            return None
        except Exception as e:
            print("Ошибка del_order : %s" % str(e))