import codecs
import logging
from configparser import ConfigParser

import discord
from discord.ext.commands import Bot
from discord_slash import SlashCommand

from util.config import Config

#   --- Config ---

TOKEN = Config.get_token()
DATA_DIR = Config.get_data_dir()

config = ConfigParser(delimiters="=")
try:
    config.read_file(codecs.open(Config.get_file(), "r", "utf8"))
except FileNotFoundError:
    fp = open(Config.get_file(), 'x')
    fp.close()
    config.read_file(codecs.open(Config.get_file(), "r", "utf8"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%d.%m.%Y %H:%M:%S")


class UniBot(Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.reactions = True
        intents.messages = True
        intents.emojis = True
        intents.bans = True
        super().__init__(command_prefix="$", help_command=None, intents=intents)

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
