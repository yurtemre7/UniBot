from main import UniBot

from .user_commands import User
from .tu_specific import TUB


def setup(bot: UniBot):
    bot.add_cog(User(bot))
    bot.add_cog(TUB(bot))
