import discord


def run_discord_bot():
    TOKEN = "MTE2NTg5NzY5OTE0NTU0Nzg2Ng.GUh0ju.-72WiaxT34_lK5Se9zakSHqQRMVNpLUz490_KY"

    WAKE_WORD = "!sum"
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
