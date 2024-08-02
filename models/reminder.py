from peewee import *
from peewee import Model, IntegerField, CharField, DateTimeField, TextField

db = SqliteDatabase('reminders.db')

class Reminder(Model):
    user_id = IntegerField()
    message = TextField()
    remind_at = DateTimeField()
    recurrence = CharField(null=True)

    class Meta:
        database = db

db.connect()
db.create_tables([Reminder])