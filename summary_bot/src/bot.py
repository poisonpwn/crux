import discord
from exceptions import MessageFetchError
from messages import MessagesFetcher, Conversation
from dotenv import dotenv_values
from summarize import Summarizer


async def get_message_fetcher(channel, exclude_predicate):
    message_fetcher = MessagesFetcher(
        channel,
        exclude_predicate,
    )
    await message_fetcher.init_message_queue()

    return message_fetcher


def run_discord_bot():
    WAKE_WORD = "!sum"
    TOKEN = dotenv_values(".env")["DISCORD_TOKEN"]
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    message_fetchers = {}
    summarizer = Summarizer()
    print("Summarizer initialized")

    def exclude_predicate(mesg):
        return mesg.content.startswith(WAKE_WORD) or mesg.author == client.user

    @client.event
    async def on_ready():
        print(f"{client.user} is now ready!")

    @client.event
    async def on_message(mesg):
        if channel_id := mesg.channel.id not in message_fetchers:
            message_fetchers[channel_id] = await get_message_fetcher(
                mesg.channel, exclude_predicate
            )

        message_fetcher = message_fetchers[channel_id]

        if mesg.author == client.user:
            return

        first_word, *fetch_bounds = str(mesg.content).split(" ")
        if first_word != WAKE_WORD:
            return

        try:
            if fetch_bounds:
                conversation_messages = message_fetcher.get_message_range(
                    *[int(bound) for bound in fetch_bounds]
                )
            else:
                conversation_messages = message_fetcher.get_till_last_message(
                    mesg.author
                )
        except MessageFetchError as e:
            await mesg.channel.send(str(e))
            return

        conversation = Conversation(conversation_messages)
        if not conversation:
            return

        summary = summarizer.summarize(str(conversation))
        try:
            await mesg.author.send(summary)
        except discord.errors.Forbidden:
            await mesg.channel.send("messaging not allowed")

    client.run(TOKEN)
