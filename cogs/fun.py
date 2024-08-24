import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import requests

class MemoryGameView(discord.ui.View):
    def __init__(self, sequence, interaction: discord.Interaction):
        super().__init__(timeout=60)
        self.sequence = sequence
        self.interaction = interaction
        self.user_sequence = []

        # Create buttons for each unique emoji in the sequence
        emoji_pool = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        available_emojis = list(set(emoji_pool) - set(sequence))  # Emojis not in the sequence
        emojis = list(set(sequence) | set(available_emojis))  # Union of correct and incorrect emojis

        # Randomize buttons
        random.shuffle(emojis)
        for emoji in emojis:
            self.add_item(MemoryGameButton(emoji, self))

    async def submit_sequence(self):
        # Check if the user's sequence matches the correct one
        if self.user_sequence == self.sequence:
            embed = discord.Embed(
                title="✅ Correct!",
                description=f"You matched the sequence correctly: {' '.join(self.sequence)}",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Incorrect!",
                description=f"The correct sequence was: {' '.join(self.sequence)}\nYour sequence: {' '.join(self.user_sequence)}",
                color=discord.Color.red()
            )

        # Disable all buttons once the sequence is submitted
        for child in self.children:
            child.disabled = True

        # Edit the original message with the results
        try:
            await self.interaction.edit_original_response(embed=embed, view=self)
        except discord.HTTPException:
            pass 

        await asyncio.sleep(5)

        end_embed = discord.Embed(
            title="Game Over",
            description="Game has ended.",
            color=discord.Color.greyple()
        )
        try:
            await self.interaction.edit_original_response(embed=end_embed, view=None)
        except discord.HTTPException:
            pass

class MemoryGameButton(discord.ui.Button):
    def __init__(self, emoji, view: MemoryGameView):
        super().__init__(label=str(emoji), style=discord.ButtonStyle.primary, emoji=emoji)
        self.memory_game_view = view

    async def callback(self, interaction: discord.Interaction):

        if interaction.user != self.memory_game_view.interaction.user:
            await interaction.response.send_message("You are not allowed to interact with this message.", ephemeral=True)
            return


        self.memory_game_view.user_sequence.append(str(self.emoji))

        if len(self.memory_game_view.user_sequence) == len(self.memory_game_view.sequence):

            await self.memory_game_view.submit_sequence()
        else:

            embed = discord.Embed(
                title="Memory Game",
                description=f"Current sequence: {' '.join(self.memory_game_view.user_sequence)}",
                color=discord.Color.blue()
            )
            try:
                await interaction.response.edit_message(embed=embed, view=self.memory_game_view)
            except discord.HTTPException:
                pass 

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="memorygame", description="Start a memory game!")
    async def memory_game(self, interaction: discord.Interaction):

        sequence_length = random.randint(5, 8)
        sequence = [str(random.choice(["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"])) for _ in range(sequence_length)]

        sequence_embed = discord.Embed(
            title="Memory Game",
            description=f"Memorize this sequence:\n{' '.join(sequence)}",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=sequence_embed)

        await asyncio.sleep(8)

        game_embed = discord.Embed(
            title="Memory Game",
            description="Now select the sequence in the correct order using the buttons below:",
            color=discord.Color.blue()
        )
        view = MemoryGameView(sequence, interaction)
        try:
            await interaction.edit_original_response(embed=game_embed, view=view)
        except discord.HTTPException:
            pass


async def setup(bot):
    await bot.add_cog(FunCommands(bot))
