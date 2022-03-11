import codecs
from configparser import ConfigParser

import discord
from discord.ext.commands import Bot, Cog, has_guild_permissions
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

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


class Admin(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = ConfigParser(delimiters="=")
        self.config.read_file(codecs.open(Config.get_file(), "r", "utf8"))

    #   --- MODLOG ---

    @has_guild_permissions(manage_roles=True)
    @cog_ext.cog_slash(name="set_modlog", guild_ids=guild_ids, description="Sets channel that is used for logs",
                       options=[
                           create_option(
                               name="channel",
                               description="Channel",
                               option_type=CHANNEL,
                               required=True
                           )
                       ])
    async def set_modlog(self, ctx: SlashContext, channel: discord.TextChannel):
        guild_id = str(ctx.guild_id)
        if not self.config.has_section(guild_id):
            self.config.add_section(guild_id)

        self.config.set(guild_id, "modlog", str(channel.id))

        with open(Config.get_file(), 'w', encoding="utf-8") as f:
            self.config.write(f)

        await ctx.send(f"Successfully set {channel.mention} as modlog", hidden=True)

    @cog_ext.cog_slash(name="get_modlog", guild_ids=guild_ids, description="Gets channel that is used for logs")
    async def get_modlog(self, ctx: SlashContext):
        guild_id = str(ctx.guild_id)
        if not self.config.has_section(guild_id) or not self.config.has_option(guild_id, "modlog"):
            await ctx.send("No modlog set", hidden=True)
        else:
            channel_id = self.config.get(guild_id, "modlog")
            channel = ctx.guild.get_channel(int(channel_id))
            await ctx.send(f"Modlog is set to {channel.mention}", hidden=True)
