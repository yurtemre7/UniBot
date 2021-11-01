import os
import codecs
import logging
from dotenv import load_dotenv
from configparser import ConfigParser

import discord
from discord.ext.commands import Bot, CommandError, Context
from discord_slash import SlashCommand

#   --- Config ---

config = ConfigParser(delimiters="=")
config.read_file(codecs.open("config.ini", "r", "utf8"))

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%d.%m.%Y %H:%M:%S")


class UniBot(Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.reactions = True
        intents.messages = True
        intents.emojis = True
        super().__init__(command_prefix="$", self_bot=True, help_command=None, intents=intents)

    async def on_ready(self):
        self.load_extension("cogs.admin")
        self.reload_extension("cogs.admin")

        self.load_extension("cogs.listeners")
        self.reload_extension("cogs.listeners")

        self.load_extension("cogs.user")
        self.reload_extension("cogs.user")

        print("Ready")
        logging.info("Startup")


def main():
    bot = UniBot()
    slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True, override_type=True)
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
