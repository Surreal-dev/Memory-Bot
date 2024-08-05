from peewee import *
from peewee import Model, IntegerField, CharField, DateTimeField, TextField

db = SqliteDatabase('memory.db')

class Reminder(Model):
    user_id = IntegerField()
    message = TextField()
    remind_at = DateTimeField()
    recurrence = CharField(null=True)
    guild_id = IntegerField(null=True)

    class Meta:
        database = db

db.connect()
db.create_tables([Reminder])