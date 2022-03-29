import codecs
from configparser import ConfigParser

from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext

from main import UniBot
from util.config import Config

guild_ids = Config.get_guild_ids()

#   --- Option Types ---

STRING = 3
INTEGER = 4
BOOLEAN = 5
USER = 6
CHANNEL = 7
ROLE = 8
MENTIONABLE = 9


class User(Cog):
    def __init__(self, bot: UniBot):
        self.bot = bot
        self.config = ConfigParser(delimiters="=")
        self.config.read_file(codecs.open(Config.get_file(), "r", "utf8"))

    @cog_ext.cog_slash(name="ping", guild_ids=guild_ids, description="Pong!")
    async def ping(self, ctx: SlashContext):
        await ctx.send("Pong!")
