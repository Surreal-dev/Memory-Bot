import discord
from discord.ext import commands, tasks
from discord import app_commands, Embed
from discord.ui import Button, View
from models.reminder import Reminder
from models.serversettings import ServerSettings
from datetime import datetime, timedelta
from utility.pagination import PaginatorView

class ReminderCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()



    @tasks.loop(seconds=60)
    async def check_reminders(self):
        now = datetime.now()

        reminders = Reminder.select().where(Reminder.remind_at <= now)

        for reminder in reminders:
            if reminder.guild_id:
                settings = ServerSettings.get_or_none(ServerSettings.guild_id == reminder.guild_id)
                if settings and settings.reminder_channel_id:
                    channel = self.bot.get_channel(settings.reminder_channel_id)
                    if channel:
                        embed = Embed(title="Server Reminder", description=reminder.message, color=discord.Color.blue())
                        embed.add_field(name="Time", value=reminder.remind_at.strftime('%Y-%m-%d %H:%M'))
                        embed.add_field(name="Recurrence", value=reminder.recurrence or 'None')
                        await channel.send(embed=embed)
            else:
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
                        embed = Embed(title="Reminder", description=reminder.message, color=discord.Color.blue())
                        embed.add_field(name="Time", value=reminder.remind_at.strftime('%Y-%m-%d %H:%M'))
                        embed.add_field(name="Recurrence", value=reminder.recurrence or 'None')
                        await user.send(embed=embed)
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

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @app_commands.command(name='setpreminder', description='Set a personal reminder')
    @app_commands.describe(date='Date of the reminder (YYYY-MM-DD)', hour='Hour of the reminder (0-23)', minute='Minute of the reminder (0-59)', message='The reminder message', recurrence='Recurrence pattern (e.g., daily, weekly, monthly)')
    async def set_reminder(self, interaction: discord.Interaction, date: str, hour: int, minute: int, message: str, recurrence: str = None):
        try:
            remind_at = datetime.strptime(f'{date} {hour}:{minute}', '%Y-%m-%d %H:%M')
            if remind_at <= datetime.now():
                await interaction.response.send_message(embed=Embed(description='The reminder time must be in the future.', color=discord.Color.red()))
                return
            Reminder.create(user_id=interaction.user.id, message=message, remind_at=remind_at, recurrence=recurrence)
            embed = Embed(title="Reminder Set", description=f"Reminder set for {remind_at.strftime('%Y-%m-%d %H:%M')}, recurring: {recurrence or 'None'}.", color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
        except ValueError:
            await interaction.response.send_message(embed=Embed(description='Invalid date, hour, or minute format. Please use YYYY-MM-DD for date, 0-23 for hour, and 0-59 for minute.', color=discord.Color.red()), ephemeral=True)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @app_commands.command(name='setsreminder', description='Set a reminder for the server')
    @app_commands.describe(date='Date of the reminder (YYYY-MM-DD)', hour='Hour of the reminder (0-23)', minute='Minute of the reminder (0-59)', message='The reminder message', recurrence='Recurrence pattern (e.g., daily, weekly, monthly)')
    async def serverreminder(self, interaction: discord.Interaction, date: str, hour: int, minute: int, message: str, recurrence: str = None):
        try:
            settings = ServerSettings.get(ServerSettings.guild_id == interaction.guild_id)
            if settings.reminder_channel_id is None or settings.reminder_role_id is None:
                await interaction.response.send_message(embed=Embed(description='Server reminder settings have not been configured. Please use the /settings command to configure them first.', color=discord.Color.red()))
                return

            role = interaction.guild.get_role(settings.reminder_role_id)
            is_owner = interaction.guild.owner_id == interaction.user.id

            if not is_owner and role not in interaction.user.roles:
                await interaction.response.send_message(embed=Embed(description=f'You do not have the required {role.mention} role to set server reminders.', color=discord.Color.red()))
                return

            remind_at = datetime.strptime(f'{date} {hour}:{minute}', '%Y-%m-%d %H:%M')
            if remind_at <= datetime.now():
                await interaction.response.send_message(embed=Embed(description='The reminder time must be in the future.', color=discord.Color.red()))
                return

            Reminder.create(user_id=interaction.user.id, message=message, remind_at=remind_at, recurrence=recurrence, guild_id=interaction.guild_id)
            embed = Embed(title="Server Reminder Set", description=f"Reminder set for {remind_at.strftime('%Y-%m-%d %H:%M')}, recurring: {recurrence or 'None'}.", color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
        except ValueError:
            await interaction.response.send_message(embed=Embed(description='Invalid date, hour, or minute format. Please use YYYY-MM-DD for date, 0-23 for hour, and 0-59 for minute.', color=discord.Color.red()))
        except ServerSettings.DoesNotExist:
            await interaction.response.send_message(embed=Embed(description='Server reminder settings have not been configured. Please use the /settings command to configure them first.', color=discord.Color.red()))

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @app_commands.command(name='listpreminders', description='List all your personal reminders')
    async def list_reminders(self, interaction: discord.Interaction):
        reminders = Reminder.select().where(Reminder.user_id == interaction.user.id, Reminder.guild_id.is_null(True)).order_by(Reminder.remind_at)
        if not reminders.exists():
            await interaction.response.send_message(embed=Embed(description='You have no personal reminders.', color=discord.Color.red()), ephemeral=True)
            return

        reminders = list(reminders)
        view = PaginatorView(reminders)
        await interaction.response.send_message(embed=view.create_embed(), view=view, ephemeral=True)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @app_commands.command(name='listsreminders', description='List all server reminders')
    async def list_server(self, interaction: discord.Interaction):
        try:
            settings = ServerSettings.get(ServerSettings.guild_id == interaction.guild_id)
            if settings.reminder_channel_id is None or settings.reminder_role_id is None:
                await interaction.response.send_message(embed=Embed(description='Server reminder settings have not been configured. Please use the /settings command to configure them first.', color=discord.Color.red()))
                return

            reminders = Reminder.select().where(Reminder.guild_id == interaction.guild_id).order_by(Reminder.remind_at)
            if not reminders.exists():
                await interaction.response.send_message(embed=Embed(description='There are no server reminders.', color=discord.Color.red()))
                return

            reminders = list(reminders)
            view = PaginatorView(reminders)
            await interaction.response.send_message(embed=view.create_embed(), view=view)
        except ServerSettings.DoesNotExist:
            await interaction.response.send_message(embed=Embed(description='Server reminder settings have not been configured. Please use the /settings command to configure them first.', color=discord.Color.red()))


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @app_commands.command(name='deletepreminder', description='Delete a personal reminder')
    @app_commands.describe(reminder_id='The ID of the reminder to delete')
    async def delete_reminder(self, interaction: discord.Interaction, reminder_id: int):
        try:
            reminder = Reminder.get(Reminder.id == reminder_id, Reminder.user_id == interaction.user.id)
            reminder.delete_instance()
            await interaction.response.send_message(embed=Embed(description=f'Reminder with ID {reminder_id} has been deleted.', color=discord.Color.green()), ephemeral=True)
        except Reminder.DoesNotExist:
            await interaction.response.send_message(embed=Embed(description=f'No reminder found with ID {reminder_id}.', color=discord.Color.red()), ephemeral=True)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @app_commands.command(name='deletesreminder', description='Delete a server reminder')
    @app_commands.describe(reminder_id='The ID of the reminder to delete')
    async def delete_server_reminder(self, interaction: discord.Interaction, reminder_id: int):
        try:
            # Fetch the server settings
            settings = ServerSettings.get(ServerSettings.guild_id == interaction.guild_id)

            # Check if the server owner or user has the required role
            if interaction.user.id != interaction.guild.owner_id and not any(role.id == settings.reminder_role_id for role in interaction.user.roles):
                await interaction.response.send_message(embed=Embed(description='You do not have the required role to delete server reminders.', color=discord.Color.red()))
                return

            # Fetch the reminder
            reminder = Reminder.get(Reminder.id == reminder_id, Reminder.guild_id == interaction.guild_id)
            reminder.delete_instance()

            embed = Embed(title='Reminder Deleted', description=f'The server reminder with ID {reminder_id} has been deleted.', color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
        
        except ServerSettings.DoesNotExist:
            await interaction.response.send_message(embed=Embed(description='Server reminder settings have not been configured. Please use the /settings command to configure them first.', color=discord.Color.red()))
        except Reminder.DoesNotExist:
            await interaction.response.send_message(embed=Embed(description='Reminder not found.', color=discord.Color.red()))
        except Exception as e:
            await interaction.response.send_message(embed=Embed(description=f'An error occurred: {str(e)}', color=discord.Color.red()))

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @app_commands.command(name='clearpreminders', description='Clear all personal reminders')
    async def clear_reminders(self, interaction: discord.Interaction):
        deleted_count = Reminder.delete().where(Reminder.user_id == interaction.user.id).execute()
        embed = Embed(title="Reminders Cleared", description=f"{deleted_count} reminders have been cleared.", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @app_commands.command(name='clearsreminders', description='Clear all server reminders')
    async def clear_server_reminders(self, interaction: discord.Interaction):
        try:
            # Fetch the server settings
            settings = ServerSettings.get(ServerSettings.guild_id == interaction.guild_id)

            # Check if the server owner or user has the required role
            if interaction.user.id != interaction.guild.owner_id and not any(role.id == settings.reminder_role_id for role in interaction.user.roles):
                await interaction.response.send_message(embed=Embed(description='You do not have the required role to clear server reminders.', color=discord.Color.red()))
                return

            # Delete all reminders for the guild
            count = Reminder.delete().where(Reminder.guild_id == interaction.guild_id).execute()

            embed = Embed(title='Reminders Cleared', description=f'All server reminders have been cleared. {count} reminders deleted.', color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
        
        except ServerSettings.DoesNotExist:
            await interaction.response.send_message(embed=Embed(description='Server reminder settings have not been configured. Please use the /settings command to configure them first.', color=discord.Color.red()))
        except Exception as e:
            await interaction.response.send_message(embed=Embed(description=f'An error occurred: {str(e)}', color=discord.Color.red()))

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @app_commands.command(name='updatepreminder', description='Update a personal reminder')
    @app_commands.describe(reminder_id='The ID of the reminder to update', date='New date (YYYY-MM-DD)', hour='New hour (0-23)', minute='New minute (0-59)', message='New message', recurrence='Recurrence pattern (e.g., daily, weekly, monthly)')
    async def update_reminder(self, interaction: discord.Interaction, reminder_id: int, date: str, hour: int, minute: int, message: str, recurrence: str = None):
        try:
            reminder = Reminder.get(Reminder.id == reminder_id, Reminder.user_id == interaction.user.id)
            
            if date and hour is not None and minute is not None:
                remind_at = datetime.strptime(f'{date} {hour}:{minute}', '%Y-%m-%d %H:%M')
                if remind_at <= datetime.now():
                    await interaction.response.send_message(embed=Embed(description='The reminder time must be in the future.', color=discord.Color.red()))
                    return
                reminder.remind_at = remind_at
            
            if message:
                reminder.message = message
            
            if recurrence:
                reminder.recurrence = recurrence

            reminder.save()
            embed = Embed(title="Reminder Updated", description=f"Reminder with ID {reminder_id} has been updated.", color=discord.Color.green())
            embed.add_field(name="Message", value=reminder.message)
            embed.add_field(name="Time", value=reminder.remind_at.strftime('%Y-%m-%d %H:%M'))
            embed.add_field(name="Recurrence", value=reminder.recurrence or 'None')
            await interaction.response.send_message(embed=embed)
        except Reminder.DoesNotExist:
            await interaction.response.send_message(embed=Embed(description=f'No reminder found with ID {reminder_id}.', color=discord.Color.red()))
        except ValueError:
            await interaction.response.send_message(embed=Embed(description='Invalid date, hour, or minute format. Please use YYYY-MM-DD for date, 0-23 for hour, and 0-59 for minute.', color=discord.Color.red()))

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @app_commands.command(name='updatesreminder', description='Update an existing server reminder')
    @app_commands.describe(reminder_id='The ID of the reminder to update', date='New date (YYYY-MM-DD)', hour='New hour (0-23)', minute='New minute (0-59)', message='New message', recurrence='Recurrence pattern (e.g., daily, weekly, monthly)')
    async def update_server_reminder(self, interaction: discord.Interaction, reminder_id: int, date: str, hour: int, minute: int, message: str, recurrence: str = None):
        try:
            # Fetch the server settings
            settings = ServerSettings.get(ServerSettings.guild_id == interaction.guild_id)

            # Check if the server owner or user has the required role
            if interaction.user.id != interaction.guild.owner_id and not any(role.id == settings.reminder_role_id for role in interaction.user.roles):
                await interaction.response.send_message(embed=Embed(description='You do not have the required role to update server reminders.', color=discord.Color.red()))
                return

            # Parse the date
            try:
                year, month, day = map(int, date.split('-'))
                new_remind_at = datetime(year, month, day, hour, minute)
            except ValueError as e:
                await interaction.response.send_message(embed=Embed(description=f'Invalid date or time: {str(e)}. Please use YYYY-MM-DD for the date.', color=discord.Color.red()))
                return
            
            if new_remind_at <= datetime.now():
                await interaction.response.send_message(embed=Embed(description='The reminder time must be set in the future.', color=discord.Color.red()))
                return

            # Fetch the reminder
            reminder = Reminder.get(Reminder.id == reminder_id, Reminder.guild_id == interaction.guild_id)

            # Update the reminder
            reminder.message = message
            reminder.remind_at = new_remind_at
            if recurrence:
                reminder.recurrence = recurrence
            reminder.save()

            embed = Embed(title='Reminder Updated', description=f'Your server reminder with ID {reminder_id} has been updated.', color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
        
        except ServerSettings.DoesNotExist:
            await interaction.response.send_message(embed=Embed(description='Server reminder settings have not been configured. Please use the /settings command to configure them first.', color=discord.Color.red()))
        except Reminder.DoesNotExist:
            await interaction.response.send_message(embed=Embed(description='Reminder not found.', color=discord.Color.red()))
        except Exception as e:
            await interaction.response.send_message(embed=Embed(description=f'An error occurred: {str(e)}', color=discord.Color.red()))


        
async def setup(bot):
    await bot.add_cog(ReminderCommands(bot))