import sqlalchemy
from models import metadata, categories
from sqlalchemy import create_engine


engine.connect()
#print(engine)


# for t in metadata.tables:
#     print(metadata.tables[t])

s = categories.select()
print(s)

conn = engine.connect()
s = categories.select()
r = conn.execute(s)
print(r.fetchall())
