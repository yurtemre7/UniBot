from discord.ext.commands import Bot

from .user_commands import User
from .tu_specific import TUB


def setup(bot: Bot):
    bot.add_cog(User(bot))
    bot.add_cog(TUB(bot))
