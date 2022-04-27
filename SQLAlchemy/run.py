import sqlalchemy
from models import metadata, categories
from sqlalchemy import create_engine
from controller import DBWorker
import controller
import os

engine = create_engine(os.environ['DBLINK'])
engine.connect()

#print(engine)


# for t in metadata.tables:
#     print(metadata.tables[t])

#s = categories.select()
#print(s)

conn = engine.connect()
w = DBWorker(conn, '2150772')
#s = w.get_lasts(4)
#s = categories.select()
#r = conn.execute(s)
#print(r.fetchall())

#s = w.get_sharp('пиво')
#r = conn.execute(s)
#rint(r.fetchall())
#print(w.del_feedback(33))
print(w.get_from_friends())