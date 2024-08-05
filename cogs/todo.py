import discord
from discord.ext import commands
from discord import app_commands, Embed
from models.todo import ToDo
from utility.pagination import ToDoPaginatorView

class ToDoCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name='addtodo', description='Add a task to your todo list')
    @app_commands.describe(task="The task to add to the list.")
    async def add_todo(self, interaction: discord.Interaction, task: str):
        # Count the current number of to-dos for the user
        todo_count = ToDo.select().where(ToDo.user_id == interaction.user.id).count()

        # Check if the user has reached the limit
        if todo_count >= 15:
            embed = Embed(title='Limit Reached', description='You can only have up to 15 tasks in your todo list.', color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Add the new task
        ToDo.create(user_id=interaction.user.id, task=task)
        embed = Embed(title='Task Added', description=f'Task "{task}" has been added to your todo list.', color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @app_commands.command(name='listtodos', description='List all tasks in your todo list')
    async def list_todos(self, interaction: discord.Interaction):
        todos = list(ToDo.select().where(ToDo.user_id == interaction.user.id))
        if not todos:
            embed = Embed(title='No Tasks', description='Your to-do list is empty.', color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            view = ToDoPaginatorView(todos, per_page=5)
            await interaction.response.send_message(embed=view.create_embed(), view=view, ephemeral=True)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @app_commands.command(name='removetodo', description='Remove a task from your todo list')
    @app_commands.describe(task_id='The ID of the task to remove from the list.')
    async def remove_todo(self, interaction: discord.Interaction, task_id: int):
        try:
            todo = ToDo.get(ToDo.id == task_id, ToDo.user_id == interaction.user.id)
            todo.delete_instance()
            embed = Embed(title='Task Removed', description=f'Task ID {task_id} has been removed from your todo list.', color=discord.Color.green())
        except ToDo.DoesNotExist:
            embed = Embed(title='Task Not Found', description=f'No task found with ID {task_id}.', color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @app_commands.command(name='completetodo', description='Mark a task as complete')
    @app_commands.describe(task_id='The ID of the task to complete.')
    async def complete_todo(self, interaction: discord.Interaction, task_id: int):
        try:
            todo = ToDo.get(ToDo.id == task_id, ToDo.user_id == interaction.user.id)
            todo.completed = True
            todo.save()
            embed = Embed(title='Task Completed', description=f'Task ID {task_id} has been marked as complete.', color=discord.Color.green())
        except ToDo.DoesNotExist:
            embed = Embed(title='Task Not Found', description=f'No task found with ID {task_id}.', color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @app_commands.command(name='cleartodo', description='Clear all tasks in your todo list')
    async def clear_todo(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        # Delete all to-do tasks for the user
        ToDo.delete().where(ToDo.user_id == user_id).execute()
        
        embed = Embed(title='To-Do List Cleared', description='All tasks in your to-do list have been cleared.', color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)



async def setup(bot):
    await bot.add_cog(ToDoCommands(bot))