import configparser
import os
import discord
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from dotenv import load_dotenv

import logging
from configparser import ConfigParser

#   --- Config ---

config = ConfigParser()
config.read("config.ini")

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


#   --- Events ---

class MyClient(discord.Client):

    async def on_ready(self):
        print("Bot ist online!")

    async def on_message(self, message: discord.Message):
        if message.author == client.user:
            return

        if "plagiat" in message.content.lower():
            await message.add_reaction("🚨")


#   --- Client Setup ---

client = MyClient()
slash = SlashCommand(client, sync_commands=True)
guild_ids = [817865198676738109]


#   --- Commands ---

@slash.slash(name="ping", guild_ids=guild_ids, description="Pong!")
async def ping(ctx: SlashContext):
    await ctx.send("Pong!")


@slash.slash(name="set_role_message", guild_ids=guild_ids, description="Set message that is use to add roles", options=[
    create_option(
        name="message_id",
        description="id of the message",
        option_type=3,  # Integer to small for message id
        required=True
    )
])
async def set_role_message(ctx: SlashContext, message_id: str):
    guild_id = str(ctx.guild_id)
    if message_id.isdigit():
        if not config.has_section(guild_id):
            config.add_section(guild_id)
        config.set(guild_id, "role_message", message_id)

        with open('config.ini', 'w') as f:
            config.write(f)

        await ctx.send(f"Set role message to {message_id}!")
    else:
        await ctx.send("Input has to be a number!")


# Hier jump_url wäre besser
@slash.slash(name="get_role_message", guild_ids=guild_ids, description="Prints id of role message")
async def get_role_message(ctx: SlashContext):
    try:
        await ctx.send(config.get(str(ctx.guild_id), "role_message"))

    except configparser.NoSectionError:
        await ctx.send("Not defined yet! Use 'set_role_message' first")


client.run(TOKEN)
logging.basicConfig()
