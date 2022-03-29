import codecs
import logging
from configparser import ConfigParser
from typing import Optional

import aiohttp
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
        self.aiohttp_session: Optional[aiohttp.ClientSession] = None
        intents = discord.Intents.default()
        intents.members = True
        intents.reactions = True
        intents.messages = True
        intents.emojis = True
        intents.bans = True
        super().__init__(command_prefix="$", help_command=None, intents=intents)

    async def on_ready(self):
        print("Ready")
        logging.info("Startup")

    async def register_aiohttp_session(self):
        self.aiohttp_session = aiohttp.ClientSession()

    def load_cogs(self) -> None:
        self.load_extension("cogs.user")
        self.load_extension("cogs.listeners")
        self.load_extension("cogs.admin")

        logging.info("loading extensions finished")

    def run_bot(self, token):
        logging.info("starting up...")
        self.load_cogs()
        self.loop.create_task(self.register_aiohttp_session())
        super().run(token)


def main():
    bot = UniBot()
    slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True, override_type=True)
    bot.run_bot(TOKEN)


if __name__ == "__main__":
    main()
