import discord


class MyClient(discord.Client):
    async def on_ready(self):
        print("Bot ist online!")

    async def on_message(self, message):



client = MyClient()
client.run("ODg2NTg0NDg1ODUwNzk2MDUz.YT3uJQ.YfP6TUt_kBJtW1b6rSKJOrCpjSE")
