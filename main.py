import random
import settings
import discord
from discord.ext import commands

logger = settings.logging.getLogger("bot")

class Slapper(commands.Converter):

    use_nicknames : bool

    def __init__(self, *, use_nicknames) -> None:
        self.use_nicknames = use_nicknames

    async def convert(self, ctx, argument):
        someone = random.choice(ctx.guild.members)
        nickname = ctx.author
        if self.use_nicknames:
            nickname = ctx.author.nick

        return f"{nickname} slaps {someone} with {argument}"

def run():
    intents = discord.Intents.default()
    intents.message_content = True


    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("handled error globally")

    @bot.command(
            aliases=['p'],
            help='This is help',
            description="This is description",
            brief='This is brief',
            enabled=True,
            hidden=True
    )
    async def ping(ctx):
        """ Answers with pong """
        await ctx.send("pong")

    @bot.command()
    async def say(ctx, what = 'WHAT?'):
        await ctx.send(what)

    @bot.command()
    async def say2(ctx, *what):
        await ctx.send(" ".join(what))

    @bot.command()
    async def choices(ctx, *options):
        await ctx.send(random.choice(options))

    @bot.command()
    async def add(ctx, one : int, two : int):
        await ctx.send(one + two)

    @bot.command()
    async def joined(ctx, who : discord.Member):
        await ctx.send(who.joined_at)

    @bot.command()
    async def slap(ctx, reason : Slapper(use_nicknames=True)):
        await ctx.send(reason)

    @bot.command()
    async def say3(ctx, what = "WHAT?", why = "WHY?"):
        await ctx.send(what + why)

    # @add.error
    # async def add_error(ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         await ctx.send("handled error locally")


    bot.run(settings.DISCORD_API_SECRET, root_logger=True)

if __name__ == "__main__":
    run()