import os
from dotenv import load_dotenv
import logging


class Config:
    @classmethod
    def get_token(cls):
        load_dotenv()
        return os.getenv('DISCORD_TOKEN')

    @classmethod
    def get_data_dir(cls):
        load_dotenv()
        return os.getenv('DATA_DIR', './data') + '/'

    @classmethod
    def get_file(cls):
        load_dotenv()
        return cls.get_data_dir() + "config.ini"

    @classmethod
    def get_guild_ids(cls):
        """
        Returns a list of guild ids to sync commands with. If 'None', commands will be globally synced.
        """
        # return [817865198676738109, 831428691870744576]
        # return [817865198676738109]
        return None
