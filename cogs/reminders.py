import discord
from discord.ext import commands, tasks
from discord import app_commands
from models.reminder import Reminder
from datetime import datetime, timedelta
import Paginator

class ReminderCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()


    @tasks.loop(seconds=60)
    async def check_reminders(self):
        now = datetime.now()

        reminders = Reminder.select().where(Reminder.remind_at <= now)

        for reminder in reminders:
            user_id = reminder.user_id
            user = self.bot.get_user(user_id)
            if not user:
                try:
                    user = await self.bot.fetch_user(user_id)  # Fetch the user from the API if not cached
                except discord.NotFound:
                    print(f"User with ID {user_id} not found.")  # Debugging statement
                    continue
                except discord.HTTPException as e:
                    print(f"HTTP error fetching user {user_id}: {e}")  # Debugging statement
                    continue

            if user:
                try:
                    await user.send(f'Reminder: {reminder.message}')
                except discord.Forbidden:
                    print(f"Failed to send reminder to {user}: Forbidden")  # Debugging statement
                except discord.HTTPException as e:
                    print(f"Failed to send reminder to {user}: HTTP error {e}")  # Debugging statement

            # Handle recurrence
            if reminder.recurrence:
                if reminder.recurrence == 'daily':
                    reminder.remind_at += timedelta(days=1)
                elif reminder.recurrence == 'weekly':
                    reminder.remind_at += timedelta(weeks=1)
                elif reminder.recurrence == 'monthly':
                    reminder.remind_at += timedelta(weeks=4)  # Approximate, for simplicity

                reminder.save()  # Update reminder with new remind_at time
            else:
                reminder.delete_instance()  # Remove the reminder after sending if not recurring


    @app_commands.command(name='setreminder', description='Set a reminder')
    @app_commands.describe(date='Date of the reminder (YYYY-MM-DD)', hour='Hour of the reminder (0-23)', minute='Minute of the reminder (0-59)', message='The reminder message', recurrence='*OPTIONAL* Recurrence pattern (e.g., daily, weekly, monthly)')
    async def set_reminder(self, interaction: discord.Interaction, date: str, hour: int, minute: int, message: str, recurrence: str = None):
        try:
            remind_at = datetime.strptime(f'{date} {hour}:{minute}', '%Y-%m-%d %H:%M')
            if remind_at <= datetime.now():
                await interaction.response.send_message('The reminder time must be in the future.')
                return
            Reminder.create(user_id=interaction.user.id, message=message, remind_at=remind_at, recurrence=recurrence)
            await interaction.response.send_message(f'Reminder set for {remind_at.strftime("%Y-%m-%d %H:%M")}, recurring: {recurrence}.')
        except ValueError:
            await interaction.response.send_message('Invalid date, hour, or minute format. Please use YYYY-MM-DD for date, 0-23 for hour, and 0-59 for minute.')


    @app_commands.command(name='listreminders', description='List all your reminders')
    async def list_reminders(self, interaction: discord.Interaction):
        reminders = Reminder.select().where(Reminder.user_id == interaction.user.id)
        if reminders:
            embeds = []
            for i, reminder in enumerate(reminders):
                embed = discord.Embed(title=f"Reminder {i+1}", description=reminder.message, color=discord.Color.blue())
                embed.add_field(name="ID", value=reminder.id)
                embed.add_field(name="Remind At", value=reminder.remind_at.strftime('%Y-%m-%d %H:%M'))
                embeds.append(embed)
            
            PreviousButton = discord.ui.Button(label="Previous", style=discord.ButtonStyle.primary)
            NextButton = discord.ui.Button(label="Next", style=discord.ButtonStyle.primary)
            InitialPage = 0 
            timeout = 60

            await Paginator.Simple(
                PreviousButton=PreviousButton,
                NextButton=NextButton,
                InitialPage=InitialPage,
                timeout=timeout).start(interaction, pages=embeds)

        else:
            await interaction.response.send_message("You have no reminders.")

    @app_commands.command(name='deletereminder', description='Delete a specific reminder by ID')
    @app_commands.describe(reminder_id='The ID of the reminder to delete')
    async def delete_reminder(self, interaction: discord.Interaction, reminder_id: int):
        try:
            reminder = Reminder.get(Reminder.id == reminder_id, Reminder.user_id == interaction.user.id)
            reminder.delete_instance()
            await interaction.response.send_message(f"Reminder {reminder_id} deleted.")
        except Reminder.DoesNotExist:
            await interaction.response.send_message(f"Reminder {reminder_id} does not exist.")

    @app_commands.command(name='clearreminders', description='Clear all your reminders')
    async def clear_reminders(self, interaction: discord.Interaction):
        Reminder.delete().where(Reminder.user_id == interaction.user.id).execute()
        await interaction.response.send_message("All your reminders have been cleared.")

    @app_commands.command(name='updatereminder', description='Update an existing reminder')
    @app_commands.describe(reminder_id='The ID of the reminder to update', date='New date of the reminder (YYYY-MM-DD)', hour='New hour of the reminder (0-23)', minute='New minute of the reminder (0-59)', message='The new reminder message')
    async def update_reminder(self, interaction: discord.Interaction, reminder_id: int, date: str, hour: int, minute: int, message: str):
        try:
            remind_at = datetime.strptime(f'{date} {hour}:{minute}', '%Y-%m-%d %H:%M')
            if remind_at <= datetime.now():
                await interaction.response.send_message('The reminder time must be in the future.')
                return
            reminder = Reminder.get(Reminder.id == reminder_id, Reminder.user_id == interaction.user.id)
            reminder.message = message
            reminder.remind_at = remind_at
            reminder.save()
            await interaction.response.send_message(f"Reminder {reminder_id} updated.")
        except Reminder.DoesNotExist:
            await interaction.response.send_message(f"Reminder {reminder_id} does not exist.")
        except ValueError:
            await interaction.response.send_message('Invalid date, hour, or minute format. Please use YYYY-MM-DD for date, 0-23 for hour, and 0-59 for minute.')

        
async def setup(bot):
    await bot.add_cog(ReminderCommands(bot))