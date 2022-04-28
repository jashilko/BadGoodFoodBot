from sqlalchemy import select, and_, desc, func, delete, union
from models import food_list, categories, user_friends

class DBWorker:
    def __init__(self, conn, user_id):
        self.user_id = user_id
        self.conn = conn
    def get_lasts(self, count):
        '''
        Получить последние записи пользователя
        '''
        s = select([
            categories.c.name,
            food_list.c.score,
            food_list.c.foto_link,
            food_list.c.descr,
            food_list.c.id
        ]).select_from(
            food_list.join(categories)
        ).where(
            food_list.c.user_id == self.user_id
        ).limit(count)
        return s

    def get_sharp(self, sharp):
        '''
        Получить 5 последних по тегу
        '''
        s = select([
            categories.c.name,
            food_list.c.score,
            food_list.c.foto_link,
            food_list.c.descr,
            food_list.c.id
        ]).select_from(
            food_list.join(categories)
        ).where(
            and_(
                food_list.c.user_id == self.user_id,
                func.upper(categories.c.name) == func.upper(sharp),
                food_list.c.score != None,
                categories.c.name != None
            )
        ).limit(5).order_by(
                desc(food_list.c.date_add)
            )
        return s

    def del_feedback(self, id_feedback):
        '''
        Удалить запись
        '''
        # Проверяем, есть ли такая запись
        s = select([
            food_list]
        ).where(
            and_(
                food_list.c.user_id == self.user_id,
                food_list.c.id == id_feedback
            )
        )
        if self.conn.execute(s).rowcount == 0:
            return "Not_Found"
        else:
            # Удаляем существующую запись
            d = delete(
                food_list
            ).where(
                and_(
                    food_list.c.user_id == self.user_id,
                    food_list.c.id == id_feedback
                )
            )
            rs = self.conn.execute(d)
            return "Ok"
    def get_from_friends(self):
        '''
        Получить отзывы свои и друзей
        '''
        # Получаем список друзей
        flist = []
        f = select([user_friends.c.friend_id]).where(user_friends.c.user_id == self.user_id)
        fe = self.conn.execute(f)
        if fe.rowcount > 0:
            row = fe.fetchall()
            flist = list(row[0])
        flist.append(int(self.user_id))
        slist = []
        for one in flist:
            s = select([
                categories.c.name,
                food_list.c.score,
                food_list.c.foto_link,
                food_list.c.descr,
                food_list.c.id
            ]).select_from(
                food_list.join(categories)
            ).where(
                food_list.c.user_id == one
            )
            slist.append(s)
        u = union(*slist)
        answers = []
        ru = self.conn.execute(u)
        results = ru.fetchone()
        while results is not None:
            answers.append({"cat": results[0], "score": results[1], "foto_link":
                results[2], "descr": results[3], "id": results[4]})
            results = ru.fetchone()
        return answers

    def get_sharp_friends(self, sharp):
        '''
        Получаем список по тегу своих и друзей
        '''
        flist = []
        f = select([user_friends.c.friend_id]).where(user_friends.c.user_id == self.user_id)
        fe = self.conn.execute(f)
        if fe.rowcount > 0:
            row = fe.fetchall()
            flist = list(row[0])
        flist.append(int(self.user_id))
        slist = []
        for one in flist:
            s = select([
                categories.c.name,
                food_list.c.score,
                food_list.c.foto_link,
                food_list.c.descr,
                food_list.c.id,
                food_list.c.user_id,
                food_list.c.date_add
            ]).select_from(
                food_list.join(categories)
            ).where(
                and_(
                    food_list.c.user_id == one,
                    func.upper(categories.c.name) == func.upper(sharp),
                    food_list.c.score != None,
                    categories.c.name != None
                )
            )
            slist.append(s)
        u = union(*slist).order_by(
                desc(food_list.c.date_add)
            )
        answers = []
        ru = self.conn.execute(u)
        results = ru.fetchone()
        while results is not None:
            answers.append({"cat": results[0], "score": results[1], "foto_link":
                results[2], "descr": results[3], "id": results[4], "user_id": results[5]})
            results = ru.fetchone()
        return answers