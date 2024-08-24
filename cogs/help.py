import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import Select, View

# Define command details manually
COMMANDS_INFO = {
    "setpreminder": {
        "description": "Set a personal reminder",
        "parameters": {
            "date": "Date of the reminder (YYYY-MM-DD).",
            "hour": "Hour of the reminder (0-23).",
            "minute": "Minute of the reminder (0-59).",
            "message": "The reminder message.",
            "recurrence": "Recurrence pattern (e.g., daily, weekly, monthly)"
        }
    },
    "setsreminder": {
        "description": "Set a server reminder",
        "parameters": {
            "date": "Date of the reminder (YYYY-MM-DD).",
            "hour": "Hour of the reminder (0-23).",
            "minute": "Minute of the reminder (0-59).",
            "message": "The reminder message.",
            "recurrence": "Recurrence pattern (e.g., daily, weekly, monthly)"
        }
    },
    "listpreminders": {
        "description": "List all your personal reminders.",
        "parameters": {}
    },
    "listsreminders": {
        "description": "List all server reminders.",
        "parameters": {}
    },
    "updatepreminder": {
        "description": "Update a personal reminder.",
        "parameters": {
            "reminder_id": "The ID of the reminder to update.",
            "date": "Date of the reminder (YYYY-MM-DD).",
            "hour": "Hour of the reminder (0-23).",
            "minute": "Minute of the reminder (0-59).",
            "message": "The reminder message.",
            "recurrence": "Recurrence pattern (e.g., daily, weekly, monthly)"
        }
    },
    "updatesreminder": {
        "description": "Update a server reminder.",
        "parameters": {
            "reminder_id": "The ID of the reminder to update.",
            "date": "Date of the reminder (YYYY-MM-DD).",
            "hour": "Hour of the reminder (0-23).",
            "minute": "Minute of the reminder (0-59).",
            "message": "The reminder message.",
            "recurrence": "Recurrence pattern (e.g., daily, weekly, monthly)"
        }
    },
    "deletepreminder": {
        "description": "Delete a personal reminder.",
        "parameters": {
            "reminder_id": "The ID of the reminder to delete."
        }
    },
    "deletesreminder": {
        "description": "Delete a server reminder.",
        "parameters": {
            "reminder_id": "The ID of the reminder to delete."
        }
    },
    "clearpreminders": {
        "description": "Clear all personal reminders.",
        "parameters": {}
    },
    "clearsreminders": {
        "description": "Clear all server reminders.",
        "parameters": {}
    },
    "addtodo": {
        "description": "Add a task to your todo list.",
        "parameters": {
            "task": "The task to add to the list"
        }
    },
    "listtodos": {
        "description": "List all tasks in your todo list.",
        "parameters": {}
    },
    "completetodo": {
        "description": "Mark a task as completed.",
        "parameters": {
            "task_id": "The ID of the task to complete."
        }
    },
    "removetodo": {
        "description": "Remove a task from your todo list.",
        "parameters": {
            "task_id": "The ID of the task to remove from the list."
        }
    },
    "cleartodo": {
        "description": "Clear all tasks in your todo list.",
        "parameters": {}
    },
    "memorygame": {
        "description": "Start a memory game!",
        "parameters": {}
    },
    "serversettings": {
        "description": "Configure server settings.",
        "parameters": {
            "channel": "The channel to send reminders in.",
            "role": "The role that can create reminders in your server."
        }
    },
    "help": {
        "description": "Shows this message.",
        "parameters": {
            "command_name": "The command you wish to see more info about."
        }
    }
}

class HelpSelect(Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Reminders", description="Commands related to reminders", value="reminders"),
            discord.SelectOption(label="To-Do List", description="Commands related to to-do lists", value="todo"),
            discord.SelectOption(label="Fun", description="Entertaining Commands", value="fun"),
            discord.SelectOption(label="Utility", description="Utility commands", value="utility")
        ]
        super().__init__(placeholder="Select a category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction):
        category = self.values[0]
        embed = discord.Embed(title=f"{category.capitalize()} Commands", color=discord.Color.blue())
        commands_info = {
            "reminders": [
                "/setpreminder",
                "/setsreminder",
                "/listpreminders",
                "/listsreminders",
                "/updatepreminder",
                "/updatesreminder",
                "/deletepreminder",
                "/deletesreminder",
                "/clearpreminders",
                "/clearsreminders"
            ],
            "todo": [
                "/addtodo",
                "/listtodos",
                "/completetodo",
                "/removetodo",
                "/cleartodo"
            ],
            "fun": [
                "/memorygame"
            ],
            "utility": [
                "/serversettings",
                "/help"
            ]
        }
        
        for command in commands_info[category]:
            command_info = COMMANDS_INFO.get(command[1:], None)  # Remove the "/" from command name
            if command_info:
                embed.add_field(name=command, value=command_info["description"], inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(View):
    def __init__(self, bot):
        super().__init__()
        self.add_item(HelpSelect(bot))


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='help', description='Show help message or info about a specific command')
    async def help_command(self, interaction: Interaction, command_name: str = None):
        if command_name:
            command_info = COMMANDS_INFO.get(command_name, None)
            if command_info:
                embed = discord.Embed(title=f"/{command_name}", description=command_info["description"], color=discord.Color.blue())
                
                # Add parameters details
                if command_info["parameters"]:
                    params = [f"**{param}**: {desc}" for param, desc in command_info["parameters"].items()]
                    embed.add_field(name="Parameters", value="\n".join(params), inline=False)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(title="Error", description=f"No command named `{command_name}` found.", color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="Help Menu", description="Select a category to view commands.", color=discord.Color.blue())
            view = HelpView(self.bot)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
