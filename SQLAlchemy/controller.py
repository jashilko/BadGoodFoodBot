from sqlalchemy import select
from models import food_list

class DBWorker:
    def __init__(self, user_id):
        self.user_id = user_id
    def get_lasts(self, count):
        '''
        Получить последние записи пользователя
        '''
        s = select([food_list])
        return s

    def get_sharp(self, sharp):
        '''
        Получить 5 последних по тегу
        '''
        pass

    def del_feedback(self, id_feedback):
        '''
        Удалить запись
        '''

