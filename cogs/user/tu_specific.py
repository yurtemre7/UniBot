import codecs

import discord
import requests
from configparser import ConfigParser
from discord.ext.commands import Bot, Cog
from discord_slash import SlashContext, cog_ext

from util.config import Config

guild_ids = Config.get_guild_ids()


class TUB(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = ConfigParser(delimiters="=")
        self.config.read_file(codecs.open(Config.get_file(), "r", "utf8"))

    @cog_ext.cog_slash(name="isis", guild_ids=guild_ids, description="Get ISIS server status")
    async def isis(self, ctx):
        error_message_isis = None
        error_message_shibboleth = None
        try:
            r_isis = requests.get("https://isis.tu-berlin.de/")
            isis_status = r_isis.status_code
        except Exception as e:
            error_message_isis = f"Error: {e}"

        try:
            r_shibboleth = requests.get(
                "https://shibboleth.tubit.tu-berlin.de/idp/profile/SAML2/Redirect/SSO?execution=e1s1")
            shibboleth_status = r_shibboleth.status_code
        except Exception as e:
            error_message_shibboleth = f"Error: {e}"

        if error_message_isis or error_message_shibboleth:
            if error_message_isis and error_message_shibboleth:
                color = 0xff0000
            else:
                color = 0xFFAD00
            embed = discord.Embed(title="ISIS Server Status", color=color, url="https://isisis.online")
            embed.add_field(name="ISIS", value=f"{error_message_isis}", inline=False)
            embed.add_field(name="Shibboleth", value=f"{error_message_shibboleth}", inline=False)
            await ctx.send(embed=embed, hidden=True)
        else:
            match (isis_status, shibboleth_status):
                case (200, 200):
                    color = 0x00ff00
                case (200, _) | (_, 200):
                    color = 0xFFAD00
                case _:
                    color = 0xFF0000

            embed = discord.Embed(title="ISIS Server Status", color=color, url="https://isisis.online")
            embed.add_field(name="ISIS", value=f"{isis_status}", inline=True)
            embed.add_field(name="Shibboleth", value=f"{shibboleth_status}", inline=True)
            await ctx.send(embed=embed, hidden=True)

    @cog_ext.cog_slash(name="autolab", guild_ids=guild_ids, description="Get Autolab server status")
    async def autolab(self, ctx: SlashContext):
        try:
            r_autolab = requests.get("https://autolab.service.tu-berlin.de/")
            autolab_status = r_autolab.status_code
            error_message = None
        except Exception as e:
            error_message = f"Error: {e}"

        if error_message:
            embed = discord.Embed(title="Autolab Server Status", color=0xff0000)
            embed.add_field(name="Error", value=f"{error_message}", inline=False)
        else:
            embed = discord.Embed(title="Autolab Server Status", color=0x00ff00,
                                  url="https://autolab.service.tu-berlin.de/")
            embed.add_field(name="Autolab", value=f"{autolab_status}", inline=True)

        await ctx.send(embed=embed, hidden=True)
