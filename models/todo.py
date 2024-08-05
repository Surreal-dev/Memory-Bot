from peewee import *
from datetime import datetime

db = SqliteDatabase('memory.db')

class ToDo(Model):
    user_id = BigIntegerField()
    task = TextField()
    completed = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db

db.connect()
db.create_tables([ToDo])