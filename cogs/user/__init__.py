from discord.ext.commands import Bot

from .user_commands import User


def setup(bot: Bot):
    bot.add_cog(User(bot))