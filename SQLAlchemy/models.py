from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, SmallInteger, ForeignKey, \
    ForeignKeyConstraint
from datetime import datetime

metadata = MetaData()

users = Table('users', metadata,
              Column('user_id', Integer(), primary_key=True),
              Column('user_name', Text()),
              Column('first_name', Text()),
              Column('last_name', Text())
)

categories = Table('categories', metadata,
                   Column('id', Integer(), primary_key=True),
                   Column('name', Text())
                   )

food_list = Table('food_list', metadata,
                  Column('id', Integer(), primary_key=True),
                  Column('user_id', Integer(), ForeignKey("users.user_id")),
                  Column('score', SmallInteger()),
                  Column('descr', Text()),
                  Column('foto_link', Text()),
                  Column('date_add', DateTime()),
                  Column('cat_id', Integer(), ForeignKey("categories.id")),
                  Column('',),
                  )

user_friends = Table('user_friends', metadata,
                     Column('id', Integer(), primary_key=True),
                     Column('user_id', Integer(), ForeignKey("users.user_id")),
                     Column('friend_id', Integer(), ForeignKey("users.user_id"))
                     )