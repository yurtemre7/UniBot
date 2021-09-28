import codecs
from configparser import ConfigParser

import discord
from discord.ext.commands import Bot, Cog, has_permissions
from discord_slash import SlashContext, cog_ext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow

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


class Admin(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = ConfigParser(delimiters="=")
        self.config.read_file(codecs.open("config.ini", "r", "utf8"))

    @cog_ext.cog_slash(name="test", guild_ids=guild_ids)
    async def test(self, ctx: SlashContext):
        await ctx.send("Hallo")

    @cog_ext.cog_slash(name="beep", guild_ids=guild_ids)
    async def test(self, ctx: SlashContext):
        buttons = [
            create_button(style=ButtonStyle.green, label="A green button"),
            create_button(style=ButtonStyle.blue, label="A blue button")
        ]
        action_row = create_actionrow(*buttons)

        await ctx.send("Hallo", components=[action_row])

    #   --- MODLOG ---

    try:
        @has_permissions(manage_roles=True)
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

            with open('config.ini', 'w', encoding="utf-8") as f:
                self.config.write(f)

            await ctx.channel.send(f"Successfully set {channel.mention} as modlog", hidden=True)

    except discord.ext.commands.errors.MissingPermissions:
        pass