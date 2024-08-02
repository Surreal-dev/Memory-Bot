from peewee import *

db = SqliteDatabase('reminders.db')

class ServerSettings(Model):
    guild_id = BigIntegerField(unique=True)
    reminder_channel_id = BigIntegerField(null=True)
    reminder_role_id = BigIntegerField(null=True)

    class Meta:
        database = db

db.connect()
db.create_tables([ServerSettings])