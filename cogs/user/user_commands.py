import codecs
from configparser import ConfigParser

from discord.ext.commands import Bot, Cog
from discord_slash import SlashContext, cog_ext

#guild_ids = [817865198676738109, 831428691870744576]
guild_ids = [817865198676738109]

#   --- Option Types ---

STRING = 3
INTEGER = 4
BOOLEAN = 5
USER = 6
CHANNEL = 7
ROLE = 8
MENTIONABLE = 9


class User(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = ConfigParser(delimiters="=")
        self.config.read_file(codecs.open("config.ini", "r", "utf8"))

    @cog_ext.cog_slash(name="ping", guild_ids=guild_ids, description="Pong!")
    async def ping(self, ctx: SlashContext):
        await ctx.send("Pong!")
