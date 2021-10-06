import codecs
import logging
from configparser import ConfigParser, NoSectionError, NoOptionError

from discord.ext.commands import Bot, Cog, has_permissions, errors
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

# guild_ids = [817865198676738109, 831428691870744576]
guild_ids = [817865198676738109]

#   --- Option Types ---

STRING = 3
INTEGER = 4
BOOLEAN = 5
USER = 6
CHANNEL = 7
ROLE = 8
MENTIONABLE = 9


class Roles(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = ConfigParser(delimiters="=")
        self.config.read_file(codecs.open("config.ini", "r", "utf8"))

    #####   set_role_message    #####
    @has_permissions(manage_roles=True)
    @cog_ext.cog_slash(name="set_role_message", guild_ids=guild_ids,
                       description="Set message that is used to add roles",
                       options=[
                           create_option(
                               name="message_link",
                               description="link to the message",
                               option_type=STRING,
                               required=True
                           )
                       ])
    async def set_role_message(self, ctx: SlashContext, message_link: str):
            guild_id = str(ctx.guild_id)
            if "https://discord.com/channels/" in message_link:
                if not self.config.has_section(guild_id):
                    self.config.add_section(str(guild_id))
                self.config.set(guild_id, "role_message", message_link)

                with open('config.ini', 'w', encoding="utf-8") as f:
                    self.config.write(f)
                    logging.info(f"{guild_id}: Set new role message to {message_link}")
                await ctx.send(f"Set role message to <{message_link}>.", hidden=True)
            else:
                await ctx.send("Error: Make sure you've got the right link", hidden=True)

    #####   get_role_message    #####
    @cog_ext.cog_slash(name="get_role_message", guild_ids=guild_ids, description="Returns link to role message")
    async def get_role_message(self, ctx: SlashContext):
        try:
            await ctx.send(self.config.get(str(ctx.guild_id), "role_message"))

        except (NoSectionError, NoOptionError):
            await ctx.send("Not defined yet! Use 'set_role_message' first", hidden=True)

    #####   add_reaction_role   #####
    @has_permissions(manage_roles=True)
    @cog_ext.cog_slash(name="add_reaction_role", guild_ids=guild_ids, description="Add emoji to assign roll",
                       options=[
                           create_option(
                               name="role",
                               description="role that should be assigned",
                               option_type=ROLE,
                               required=True
                           ),
                           create_option(
                               name="emoji",
                               description="emoji that is used to assign the role",
                               option_type=STRING,
                               required=True
                           )
                       ])
    async def add_reaction_role(self, ctx: SlashContext, role: str, emoji: str):
        guild_id = str(ctx.guild_id)

        if not self.config.has_option(guild_id, "role_message"):
            await ctx.send("Please define a role message first. Use set_role_message", hidden=True)

        link = self.config.get(guild_id, "role_message").split('/')

        channel_id = int(link[5])
        msg_id = int(link[6])

        channel = self.bot.get_channel(channel_id)
        msg = await channel.fetch_message(msg_id)

        self.config.set(guild_id, str(emoji), str(role))
        try:
            with open('config.ini', 'w', encoding='utf-8') as f:
                self.config.write(f)

            await msg.add_reaction(emoji)
            await ctx.send(f"Successfully added role \'{role}\'", hidden=True)
        except errors.HTTPException:
            self.config.remove_option(guild_id, str(emoji))
            with open('config.ini', 'w', encoding='utf-8') as f:
                self.config.write(f)
            await ctx.send("Error: Make sure you only use standard emojis or emojis from this server", hidden=True)

    # TODO:
    #####   remove_reaction_role    #####
    #####   remove_role_message     #####
