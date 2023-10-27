import discord
from dotenv import dotenv_values



def run_discord_bot():
    WAKE_WORD = "!sum"
    TOKEN = dotenv_values(".env")["DISCORD_TOKEN"]
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"{client.user} is now ready!")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        user_message = str(message.content)
        if not user_message.startswith(WAKE_WORD):
            return

        user_message = user_message[len(WAKE_WORD) + 1 :]
        print(user_message)

        if user_message == "hello":
            response = "Hi"
            await message.channel.send(response)

    client.run(TOKEN)
