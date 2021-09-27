from discord.ext.commands import Bot

from .event_listeners import Listen


def setup(bot: Bot):
    bot.add_cog(Listen(bot))
