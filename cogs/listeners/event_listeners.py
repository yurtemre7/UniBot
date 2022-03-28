import json
import codecs
import logging
from configparser import ConfigParser
from datetime import datetime

import discord
from discord.ext.commands import Bot, Cog

from util.config import Config


class Listen(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = ConfigParser(delimiters="=")
        self.config.read_file(codecs.open(Config.get_file(), "r", "utf8"))

    # Fun
    @Cog.listener()
    async def on_message(self, message: discord.Message):

        logging.info(f"{message.author}: {message.content}")

        if message.author.id == self.bot.user.id:
            return

        if "plagiat" in message.content.lower():
            await message.add_reaction("🚨")

    # Reaction Roles
    @Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        self.config.read_file(codecs.open(Config.get_file(), "r", "utf8"))  # Make sure data is up to date

        guild_id = str(payload.guild_id)
        channel_id = str(payload.channel_id)
        message_id = str(payload.message_id)
        emoji = str(payload.emoji)

        if self.config.has_option(guild_id, f"{message_id}_{emoji}"):
            guild = self.bot.get_guild(int(guild_id))
            role_string = self.config.get(guild_id, f"{message_id}_{emoji}")
            role = discord.utils.get(guild.roles, name=role_string)
            member = await guild.fetch_member(payload.user_id)

            await member.add_roles(role)

    # Reaction Roles
    @Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        guild_id = str(payload.guild_id)
        channel_id = str(payload.channel_id)
        message_id = str(payload.message_id)
        emoji = str(payload.emoji)

        self.config.read_file(codecs.open(Config.get_file(), "r", "utf8"))  # Make sure data is up to date

        if self.config.has_option(guild_id, f"{message_id}_{emoji}"):
            guild = self.bot.get_guild(int(guild_id))
            role_string = self.config.get(guild_id, f"{message_id}_{emoji}")
            role = discord.utils.get(guild.roles, name=role_string)
            member = await guild.fetch_member(payload.user_id)

            await member.remove_roles(role)

    # If multiple messages of the same target are deleted by the same person in a short time, only the first delete
    # will get reported, as discord does not send a new audit log entry, only updates the old one
    # could not find a timestamp for audit log updates, only for new entries
    @Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        guild_id = str(message.guild.id)

        # Log messages deleted by mods
        logging.info(f"Delete {message.author}'s message: {message.content}")
        if (not message.author.bot) and self.config.has_option(guild_id, "modlog"):
            try:
                async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
                    author_can_delete_massages = message.author.permissions_in(message.channel).manage_messages
                    timestamp = entry.created_at

                    if (datetime.utcnow() - timestamp).total_seconds() < 1.0 and not author_can_delete_massages:

                        embed = discord.Embed(title="Message Deleted By Mod")
                        embed.add_field(name="Member: ", value=message.author.mention, inline=True)
                        embed.add_field(name="Mod: ", value=entry.user.mention, inline=True)

                        # Media might not have message content
                        if message.content:
                            embed.add_field(name="Message: ", value=message.content, inline=False)
                        else:
                            embed.add_field(name="Message: ", value="None", inline=False)

                        embed.add_field(name="Channel: ", value=message.channel.mention, inline=False)

                        # List of media urls, display first image
                        if message.attachments:
                            links = "".join(str(url) + "\n" for url in message.attachments)
                            embed.add_field(name="Media: ", value=links, inline=False)
                            embed.set_image(url=message.attachments[0])

                        self.config.read_file(
                            codecs.open(Config.get_file(), "r", "utf8"))  # Make sure data is up to date
                        modlog_id = self.config.get(guild_id, "modlog")
                        modlog = await self.bot.fetch_channel(modlog_id)
                        logging.info("Sending message delete log")
                        await modlog.send(embed=embed)
                        return

            except discord.errors.Forbidden:
                logging.warning("Missing permissions for logging message deletion")

        # Watch Users
        watched_users = json.loads(self.config.get(guild_id, "watched_users", fallback="[]"))
        watched_dict = json.loads(self.config.get(guild_id, "watched_dict", fallback="{}"))
        if message.author.id in watched_users:
            channel = await self.bot.fetch_channel(watched_dict[str(message.author.id)])
            embed = discord.Embed(description=message.content, type="rich")
            embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            embed.set_footer(text=f"#{message.channel.name}")
            await channel.send(embed=embed)

    @Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        guild_id = str(guild.id)
        if self.config.has_option(guild_id, "modlog"):
            try:
                async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                    logging.info(entry)
                    embed = discord.Embed(title="Member Banned", color=discord.Color.red())
                    embed.add_field(name="Member: ", value=user.mention, inline=True)
                    embed.add_field(name="Mod: ", value=entry.user.mention, inline=True)

                    self.config.read_file(
                        codecs.open(Config.get_file(), "r", "utf8"))  # Make sure data is up to date
                    modlog_id = self.config.get(guild_id, "modlog")
                    modlog = await self.bot.fetch_channel(modlog_id)
                    logging.info("Sending member ban log")
                    await modlog.send(embed=embed)

            except discord.errors.Forbidden:
                logging.warning("Missing permissions for logging member ban")

    @Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        guild_id = str(guild.id)
        if self.config.has_option(guild_id, "modlog"):
            try:
                async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
                    embed = discord.Embed(title="Member Unbanned", color=discord.Color.red())
                    embed.add_field(name="Member: ", value=user.mention, inline=True)
                    embed.add_field(name="Mod: ", value=entry.user.mention, inline=True)

                    self.config.read_file(
                        codecs.open(Config.get_file(), "r", "utf8"))  # Make sure data is up to date
                    modlog_id = self.config.get(guild_id, "modlog")
                    modlog = await self.bot.fetch_channel(modlog_id)
                    logging.info("Sending member unban log")
                    await modlog.send(embed=embed)

            except discord.errors.Forbidden:
                logging.warning("Missing permissions for logging member unban")
