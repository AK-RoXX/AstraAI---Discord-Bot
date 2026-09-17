import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from ai.llm import generate_response
from ai.context import get_channel_context


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")


intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():

    print(f"Logged in as {bot.user}")
    print(f"Connected to {len(bot.guilds)} server(s)")


@bot.command()
async def hello(ctx):

    await ctx.send(
        "Hello! Astra is online 🤖"
    )


@bot.event
async def on_message(message):

    # Ignore Astra's own messages
    if message.author == bot.user:
        return

    # Process normal commands such as !hello
    await bot.process_commands(message)

    # Only respond when Astra is mentioned
    if bot.user not in message.mentions:
        return

    # Remove the mention from the message
    user_message = message.content

    for mention in message.mentions:
        user_message = user_message.replace(
            f"<@{mention.id}>",
            ""
        )

    user_message = user_message.strip()

    if not user_message:
        await message.channel.send(
            "Ask me something 🤖"
        )
        return

    channel_name = message.channel.name

    system_prompt = get_channel_context(
        channel_name
    )

    system_prompt += """

You are operating inside Discord.

Keep responses reasonably concise.
Use Markdown when useful.
Do not claim to have searched the internet unless
an actual search tool was used.
"""

    async with message.channel.typing():

        try:

            response = await generate_response(
                system_prompt=system_prompt,
                user_message=user_message,
            )

            # Discord messages have a 2000 character limit
            if len(response) <= 2000:

                await message.channel.send(response)

            else:

                for i in range(
                    0,
                    len(response),
                    1900
                ):

                    await message.channel.send(
                        response[i:i + 1900]
                    )

        except Exception as e:

            print("AI ERROR:", e)

            await message.channel.send(
                "⚠️ I couldn't reach the AI model."
            )


bot.run(TOKEN)