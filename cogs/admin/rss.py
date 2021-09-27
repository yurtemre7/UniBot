import codecs
from configparser import ConfigParser
import codecs
import logging
import feedparser
import html2text
from configparser import ConfigParser

import discord
from discord.ext.commands import Bot, Cog, has_permissions
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

guild_ids = [817865198676738109, 831428691870744576]

#   --- Option Types ---

STRING = 3
INTEGER = 4
BOOLEAN = 5
USER = 6
CHANNEL = 7
ROLE = 8
MENTIONABLE = 9


class RSS(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = ConfigParser(delimiters="=")
        self.config.read_file(codecs.open("config.ini", "r", "utf8"))

    try:
        @has_permissions(manage_roles=True)
        @cog_ext.cog_slash(name="add_rss_feed", guild_ids=guild_ids, description="Setup a rss feed for this channel",
                     options=[
                         create_option(
                             name="feed_link",
                             description="link to rss feed",
                             option_type=STRING,
                             required=True
                         ),
                         create_option(
                             name="role",
                             description="role to ping on rss update",
                             option_type=ROLE,
                             required=False
                         )
                     ])
        async def add_rss_feed(self, ctx: SlashContext, feed_link: str, role: discord.role = None):
            guild_id = str(ctx.guild_id)
            channel_id = str(ctx.channel.id)

            if not self.config.has_section(guild_id):
                self.config.add_section(str(guild_id))

            if not self.config.has_option(guild_id, "rss_channels"):
                self.config.set(guild_id, "rss_channels", channel_id)
            else:
                channels = self.config.get(guild_id, "rss_channels").split(",")
                if channel_id not in channels:
                    self.config.set(guild_id, "rss_channels", f"{self.config.get(guild_id, 'rss_channels')},{channel_id}")

            self.config.set(guild_id, f"{channel_id}_link", feed_link)
            if role:
                self.config.set(guild_id, f"{channel_id}_role", role.name)

            with open('config.ini', 'w', encoding="utf-8") as f:
                self.config.write(f)
                logging.info(f"{guild_id}: Added rss feed for channel {channel_id}")
            await ctx.send("Added new rss feed.", hidden=True)
    except discord.ext.commands.errors.MissingPermissions:
        pass

    try:
        @has_permissions(manage_roles=True)
        @cog_ext.cog_slash(name="load_rss", guild_ids=guild_ids, description="Load newest rss entry",
                     options=[
                         create_option(
                             name="ping",
                             description="ping according role",
                             option_type=BOOLEAN,
                             required=False
                         )
                     ])
        async def load_rss(self, ctx: SlashContext, ping=False):
            guild_id = str(ctx.guild_id)
            channel_id = str(ctx.channel.id)

            if (not self.config.has_section(guild_id)) or (not self.config.has_option(guild_id, f"{channel_id}_link")):
                await ctx.send("No rss feed has been setup yet", hidden=True)
                return

            if ping:
                role = self.config.get(guild_id, f"{channel_id}_role")
            else:
                role = None

            await send_rss_entry(self.bot, int(channel_id), self.config.get(guild_id, f"{channel_id}_link"), role=role)

    except discord.ext.commands.errors.MissingPermissions:
        pass

# https://github.com/zenxr/discord_rss_bot
async def send_rss_entry(bot: Bot, channel_id: int, link: str, role: str = None):
    d = feedparser.parse(link)
    channel = bot.get_channel(channel_id)

    post = d.entries[0]
    title = (post.title.encode('utf-8', 'ignore').decode('utf-'))
    html = (post.summary.encode('utf-8', 'ignore').decode('utf-8'))
    text = html2text.html2text(html)
    link = post.link

    if len(text) > 1024:
        text = text[:1018] + "\n[...]"

    embed = discord.Embed(title=title)
    embed.add_field(name="Text: ", value=text, inline=False)
    embed.add_field(name="Link: ", value=link, inline=False)


    logging.info(f"New rss entry for channel {channel_id}")
    await channel.send(embed=embed)
    if role:
        await channel.send(discord.utils.get(channel.guild.roles, name=role).mention)