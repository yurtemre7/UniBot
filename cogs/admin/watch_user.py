import json
import codecs
import logging
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


class WatchUser(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = ConfigParser(delimiters="=")
        self.config.read_file(codecs.open(Config.get_file(), "r", "utf8"))

    @has_guild_permissions(manage_roles=True)
    @cog_ext.cog_slash(name="watch", guild_ids=guild_ids, description="Add user to watch list",
                       options=[
                           create_option(
                               name="user",
                               description="User",
                               option_type=USER,
                               required=True
                           )
                       ])
    async def watch(self, ctx: SlashContext, user: discord.User):
        guild_id = str(ctx.guild_id)
        if not self.config.has_section(guild_id):
            self.config.add_section(guild_id)

        watched_users = json.loads(self.config.get(guild_id, "watched_users", fallback="[]"))
        watched_dict = json.loads(self.config.get(guild_id, "watched_dict", fallback="{}"))

        if user.id in watched_users:
            await ctx.send(f"{user.mention} is already on the watch list", hidden=True)
        else:

            category_id = self.config.get(guild_id, "watch_category", fallback=None)
            if valid_category := category_id and discord.utils.get(
                ctx.guild.categories, id=int(category_id)
            ):
                watch_category = discord.utils.get(ctx.guild.categories, id=int(category_id))
                new_channel = await ctx.guild.create_text_channel(name=f"{user.name}", category=watch_category)
                watched_dict[str(user.id)] = str(new_channel.id)

                watched_users.append(user.id)
                self.config.set(guild_id, "watched_users", str(watched_users))
                self.config.set(guild_id, "watched_dict", json.dumps(watched_dict))

                with open(Config.get_file(), 'w', encoding="utf-8") as f:
                    self.config.write(f)

                await new_channel.send(
                    f"{ctx.author.mention} added {user.mention} to the watch list. Use /unwatch to remove them.")
                await new_channel.send(
                    "Do not manually delete this channel. "
                    "It will be deleted automatically when the user gets removed from the watch list.")

                await ctx.send(f"Successfully added {user.mention} to watch list, see {new_channel.mention}",
                               hidden=True)
            else:
                await ctx.send("Please set a category for the new channels first. Use /watch_category.",
                               hidden=True)

    @has_guild_permissions(manage_roles=True)
    @cog_ext.cog_slash(name="unwatch", guild_ids=guild_ids, description="Remove user from watch list",
                       options=[
                           create_option(
                               name="user",
                               description="User",
                               option_type=USER,
                               required=True
                           ),
                           create_option(
                               name="delete",
                               description="Delete channel?",
                               option_type=BOOLEAN,
                               required=True
                           )
                       ])
    async def unwatch(self, ctx: SlashContext, user: discord.User, delete: bool):
        guild_id = str(ctx.guild_id)

        watched_users = json.loads(self.config.get(guild_id, "watched_users", fallback="[]"))
        watched_dict = json.loads(self.config.get(guild_id, "watched_dict", fallback="{}"))

        if user.id not in watched_users:
            await ctx.send(f"{user.mention} is not on the watch list", hidden=True)
        else:

            watched_users.remove(user.id)
            channel_id = int(watched_dict.pop(str(user.id)))
            if delete:
                await ctx.guild.get_channel(channel_id).delete()
            else:
                await ctx.guild.get_channel(channel_id).send(
                    f"User {user.mention} has been removed from the watch list by {ctx.author.mention}."
                    f" You can delete this channel at any time.")

            self.config.set(guild_id, "watched_users", str(watched_users))
            self.config.set(guild_id, "watched_dict", json.dumps(watched_dict))

            with open(Config.get_file(), 'w', encoding="utf-8") as f:
                self.config.write(f)

            await ctx.send(f"Successfully removed {user.mention} from watch list", hidden=True)

    @has_guild_permissions(manage_roles=True)
    @cog_ext.cog_slash(name="watched", guild_ids=guild_ids, description="Gets users that are on watch list")
    async def watched(self, ctx: SlashContext):
        guild_id = str(ctx.guild_id)
        if not self.config.has_section(guild_id) or not self.config.has_option(guild_id, "watched_users"):
            await ctx.send("No watched users set", hidden=True)
        else:
            watched_users = json.loads(self.config.get(guild_id, "watched_users", fallback="[]"))
            watched_dict = json.loads(self.config.get(guild_id, "watched_dict", fallback="{}"))

            if len(watched_users) == 0:
                await ctx.send("No watched users", hidden=True)
            else:
                embed = discord.Embed(title="Watched users")
                too_long = len(watched_users) > 25
                if too_long:
                    watched_users = watched_users[:24]

                for user_id in watched_users:
                    if user := self.bot.get_user(user_id):
                        embed.add_field(name=user.name,
                                        value=
                                        f"{user.mention} "
                                        f"({ctx.guild.get_channel(int(watched_dict[str(user.id)])).mention})",
                                        inline=False)
                    else:
                        embed.add_field(name=user_id,
                                        value=
                                        "User not found "
                                        f"({ctx.guild.get_channel(int(watched_dict.pop(str(user_id)))).mention})",
                                        inline=False)

                if too_long:
                    embed.add_field(name="...", value="...", inline=False)
                await ctx.send(embed=embed, hidden=True)

    @has_guild_permissions(manage_roles=True)
    @cog_ext.cog_slash(name="watch_category", guild_ids=guild_ids, description="Set category for watch list",
                       options=[
                           create_option(
                               name="category",
                               description="Category",
                               option_type=discord.CategoryChannel,
                               required=True
                           )
                       ])
    async def watch_category(self, ctx: SlashContext, category: discord.CategoryChannel):
        guild_id = str(ctx.guild_id)
        if not self.config.has_section(guild_id):
            self.config.add_section(guild_id)

        self.config.set(guild_id, "watch_category", str(category.id))

        with open(Config.get_file(), 'w', encoding="utf-8") as f:
            self.config.write(f)

        await ctx.send(f"Successfully set watch category to {category.mention}", hidden=True)
