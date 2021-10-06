import codecs
import logging
from configparser import ConfigParser
from datetime import datetime

import discord
from discord.ext.commands import Bot, Cog


class Listen(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = ConfigParser(delimiters="=")
        self.config.read_file(codecs.open("config.ini", "r", "utf8"))

    @Cog.listener()
    async def on_message(self, message: discord.Message):

        logging.info(f"{message.author}: {message.content}")

        if message.author.id == self.bot.user.id:
            return

        if "plagiat" in message.content.lower():
            await message.add_reaction("🚨")

    # If multiple messages of the same target are deleted by the same person in a short time, only the first delete
    # will get reported, as discord does not send a new audit log entry, only updates the old one
    # could not find a timestamp for audit log updates, only for new entries
    @Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        guild_id = str(message.guild.id)
        logging.info(f"Delete {message.author}'s message: {message.content}")
        if (not message.author.bot) and self.config.has_option(guild_id, "modlog"):
            try:
                async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
                    author_can_delete_massages = message.author.permissions_in(message.channel).manage_messages
                    timestamp = entry.created_at
                    if author_can_delete_massages:
                        return

                    if (datetime.utcnow() - timestamp).total_seconds() < 1.0:

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
                            links = ""
                            for url in message.attachments:
                                links += str(url) + "\n"
                            embed.add_field(name="Media: ", value=links, inline=False)
                            embed.set_image(url=message.attachments[0])

                        self.config.read_file(codecs.open("config.ini", "r", "utf8"))   # Make sure data is up to date
                        modlog_id = self.config.get(guild_id, "modlog")
                        modlog = await self.bot.fetch_channel(modlog_id)
                        logging.info("Sending message delete log")
                        await modlog.send(embed=embed)

            except discord.errors.Forbidden:
                logging.warning("Missing permissions for logging message deletion")

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        self.config.read_file(codecs.open("config.ini", "r", "utf8"))

        guild_id = str(payload.guild_id)
        channel_id = str(payload.channel_id)
        message_id = str(payload.message_id)
        link = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
        emoji = str(payload.emoji)
        print(f"{link}: {emoji}")
        if self.config.has_option(guild_id, "role_message"):
            role_link = self.config.get(guild_id, "role_message")   # Make sure data is up to date
            if (role_link == link) and self.config.has_option(guild_id, emoji):
                guild = self.bot.get_guild(int(guild_id))
                role_string = self.config.get(guild_id, emoji)
                role = discord.utils.get(guild.roles, name=role_string)
                member = await guild.fetch_member(payload.user_id)

                await member.add_roles(role)

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        guild_id = str(payload.guild_id)
        channel_id = str(payload.channel_id)
        message_id = str(payload.message_id)
        link = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
        emoji = str(payload.emoji)

        if self.config.has_option(guild_id, "role_message"):
            if (self.config.get(guild_id, "role_message") == link) and (self.config.has_option(guild_id, emoji)):
                guild = self.bot.get_guild(int(guild_id))
                role_string = self.config.get(guild_id, emoji)
                role = discord.utils.get(guild.roles, name=role_string)
                member = await guild.fetch_member(payload.user_id)

                await member.remove_roles(role)
