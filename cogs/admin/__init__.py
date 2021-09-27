from discord.ext.commands import Bot

from .admin_commands import Admin
from .roles import Roles
from .rss import RSS


def setup(bot: Bot):
    bot.add_cog(Admin(bot))
    bot.add_cog(Roles(bot))
    bot.add_cog(RSS(bot))
