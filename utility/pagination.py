import discord
from discord import Embed
from discord.ui import Button, View

class PaginatorView(View):
    def __init__(self, reminders, per_page=2):
        super().__init__()
        self.reminders = reminders
        self.per_page = per_page
        self.current_page = 0
        self.total_pages = (len(reminders) - 1) // per_page + 1
        self.update_buttons()

    def update_buttons(self):
        self.first_page.disabled = self.current_page == 0
        self.previous_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page >= self.total_pages - 1
        self.last_page.disabled = self.current_page >= self.total_pages - 1

    def create_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        reminders_slice = self.reminders[start:end]

        embed = Embed(title="Reminders", color=discord.Color.blue())
        for reminder in reminders_slice:
            embed.add_field(name=f"ID: {reminder.id}", value=f"Message: {reminder.message}\nTime: {reminder.remind_at.strftime('%Y-%m-%d %H:%M')}\nRecurrence: {reminder.recurrence or 'None'}", inline=False)
        return embed

    async def update_embed(self, interaction: discord.Interaction):
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="<<", style=discord.ButtonStyle.gray)
    async def first_page(self, interaction: discord.Interaction, button: Button):
        self.current_page = 0
        self.update_buttons()
        await self.update_embed(interaction)

    @discord.ui.button(label="<", style=discord.ButtonStyle.gray)
    async def previous_page(self, interaction: discord.Interaction, button: Button):
        self.current_page -= 1
        self.update_buttons()
        await self.update_embed(interaction)

    @discord.ui.button(label=">", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        self.current_page += 1
        self.update_buttons()
        await self.update_embed(interaction)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.gray)
    async def last_page(self, interaction: discord.Interaction, button: Button):
        self.current_page = self.total_pages - 1
        self.update_buttons()
        await self.update_embed(interaction)



# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



class ToDoPaginatorView(View):
    def __init__(self, todos, per_page=5):
        super().__init__()
        self.todos = todos
        self.per_page = per_page
        self.current_page = 0
        self.total_pages = (len(todos) - 1) // per_page + 1
        self.update_buttons()

    def update_buttons(self):
        self.first_page.disabled = self.current_page == 0
        self.previous_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page >= self.total_pages - 1
        self.last_page.disabled = self.current_page >= self.total_pages - 1

    def create_embed(self):
        start = self.current_page * self.per_page
        end = start + self.per_page
        todos_slice = self.todos[start:end]

        embed = Embed(title="To-Do List", color=discord.Color.blue())
        for todo in todos_slice:
            status = '✅' if todo.completed else '❌'
            embed.add_field(name=f"ID: {todo.id}", value=f"Task: {todo.task}\nStatus: {status}\nCreated At: {todo.created_at.strftime('%Y-%m-%d %H:%M')}", inline=False)
        return embed

    async def update_embed(self, interaction: discord.Interaction):
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="<<", style=discord.ButtonStyle.gray)
    async def first_page(self, interaction: discord.Interaction, button: Button):
        self.current_page = 0
        self.update_buttons()
        await self.update_embed(interaction)

    @discord.ui.button(label="<", style=discord.ButtonStyle.gray)
    async def previous_page(self, interaction: discord.Interaction, button: Button):
        self.current_page -= 1
        self.update_buttons()
        await self.update_embed(interaction)

    @discord.ui.button(label=">", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        self.current_page += 1
        self.update_buttons()
        await self.update_embed(interaction)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.gray)
    async def last_page(self, interaction: discord.Interaction, button: Button):
        self.current_page = self.total_pages - 1
        self.update_buttons()
        await self.update_embed(interaction)
