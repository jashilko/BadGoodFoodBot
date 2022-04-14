import sqlalchemy
from models import metadata, categories
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://knqprsizhfmhvo:06eac893975210ab6778d1efaa96f0e5536c71b20a244a6496309d53401514b9@ec2-44-199-83-229.compute-1.amazonaws.com/d55qo5k71vl8lg")

engine.connect()
#print(engine)

# #database = PostgresqlDatabase('d55qo5k71vl8lg', user='knqprsizhfmhvo',
#                               password='06eac893975210ab6778d1efaa96f0e5536c71b20a244a6496309d53401514b9',
#                               host='ec2-44-199-83-229.compute-1.amazonaws.com')

# for t in metadata.tables:
#     print(metadata.tables[t])

s = categories.select()
print(s)

conn = engine.connect()
s = categories.select()
r = conn.execute(s)
print(r.fetchall())