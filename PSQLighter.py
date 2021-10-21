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
            self.user_id = None
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
                self.cursor.execute('''insert into food_list(user_id) values(%s) RETURNING id''' % (self.user_id) )
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
                self.check_exist_client(message.from_user)
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
            print("Ошибка get_category_id: %s" % str(e))

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
                self.check_exist_client(message.from_user)
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

    def set_photo(self, message):
        try:
            if self.user_id is None:
                self.check_exist_client(message.from_user)
            if self.id_feedback is None:
                self.create_feedback_id()
            with self.connection:
                 self.cursor.execute('''UPDATE food_list SET foto_link = \'%s\' WHERE id = %s;''' % (
                     message.photo[-1].file_id, self.id_feedback))
                 self.connection.commit
        except Exception as e:
            print("Ошибка set_photo: %s" % str(e))

    def get_lasts(self, message):
        try:
            if self.user_id is None:
                self.check_exist_client(message.from_user)
            cursor = self.connection.cursor()
            cursor.execute('''select categories.name, score, foto_link, descr 
            from food_list left join categories on food_list.cat_id = categories.id 
            where user_id = %s order by date_add desc limit %s''' % (self.user_id, message.text))
            answers = []
            results = cursor.fetchone()
            while results is not None:
                answers.append({"cat": results[0], "score": results[1], "foto_link":
                                results[2], "descr": results[3]})
                results = cursor.fetchone()
            return answers
        except Exception as e:
            print("Ошибка get_lasts: %s" % str(e))
