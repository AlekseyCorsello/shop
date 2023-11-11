from peewee import PostgresqlDatabase
from peewee import Model
from peewee import CharField
from peewee import TextField
from peewee import DoubleField
from peewee import BooleanField
from peewee import DateField
from peewee import ForeignKeyField

from config import POSTGRES_PASSWORD
from datetime import datetime

pg_db = PostgresqlDatabase('shop_db',
        user='postgres',
        password=POSTGRES_PASSWORD,
        host='localhost')

class Base(Model):
    """A base model that will use our Postgresql database"""
    class Meta:
        database = pg_db

class UserRole(Base):
    name = CharField(max_length=20)

class User(Base):
    first_name = CharField(max_length=20)
    last_name = CharField(max_length=20)
    email = CharField(max_length=50, unique=True)
    password = CharField(max_length=30)
    role = ForeignKeyField(UserRole)

class Category(Base):
    name = CharField(max_length=20, unique=True)

class Product(Base):
    name = CharField(max_length=200, unique=True)
    photo = CharField()
    category = ForeignKeyField(Category)
    price = DoubleField()
    description = TextField()

class Order(Base):
    customer = ForeignKeyField(User, backref='orders')
    product = ForeignKeyField(Product)
    date = DateField(default=datetime.today)
    status = CharField(max_length=20)

if __name__ == '__main__':
    pg_db.create_tables([UserRole, User, Category, Product, Order])

    UserRole.create(name = 'admin')
    UserRole.create(name = 'user')

    User.create(
        first_name = 'admin',
        last_name = 'admin',
        email = 'admin@admin.ru',
        password = '12345',
        role = UserRole.select().where(UserRole.name == 'admin')
    )