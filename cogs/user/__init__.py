from main import UniBot
from .tu_specific import TUB
from .user_commands import User


def setup(bot: UniBot):
    bot.add_cog(User(bot))
    bot.add_cog(TUB(bot))
