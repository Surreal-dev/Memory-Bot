import discord
from discord.ext import commands, tasks
from discord import app_commands, Embed
from models.serversettings import ServerSettings


class ServerCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='settings', description='Configure server reminder settings')
    async def settings(self, interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role):
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message(embed=Embed(description='Only the server owner can use this command.', color=discord.Color.red()))
            return

        try:
            settings, created = ServerSettings.get_or_create(guild_id=interaction.guild_id)
            if channel:
                settings.reminder_channel_id = channel.id
            if role:
                settings.reminder_role_id = role.id

            settings.save()

            embed = Embed(title='Settings Updated', description='The server reminder settings have been updated.', color=discord.Color.green())
            if channel:
                embed.add_field(name='Reminder Channel', value=channel.mention, inline=False)
            if role:
                embed.add_field(name='Reminder Role', value=role.mention, inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(embed=Embed(description=f'Error updating settings: {e}', color=discord.Color.red()))


async def setup(bot):
    await bot.add_cog(ServerCommands(bot))