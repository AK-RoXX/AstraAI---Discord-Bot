import os
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ai.llm import generate_response
from ai.context import get_channel_context, channel_key
from memory.database import init_db, save_message, get_recent_messages, save_summary, get_summary
from services.news import fetch_news, format_news_for_discord
from services.youtube import recommend_videos
from services.dsa import get_daily_dsa
from services.anime import get_anime_image

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

INTEL_CHANNEL_ID = os.getenv("INTEL_CHANNEL_ID")
LEARNING_CHANNEL_ID = os.getenv("LEARNING_CHANNEL_ID")
DSA_CHANNEL_ID = os.getenv("DSA_CHANNEL_ID")
ANIME_CHANNEL_ID = os.getenv("ANIME_CHANNEL_ID")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler(timezone=TIMEZONE)


def configured_channel_id(value):
    try:
        return int(value) if value else None
    except ValueError:
        return None


async def send_long(channel, text):
    if len(text) <= 1900:
        await channel.send(text)
        return
    for i in range(0, len(text), 1900):
        await channel.send(text[i:i+1900])


async def ai_answer(channel, user, question):
    key = channel_key(channel)
    system = get_channel_context(key)
    recent = await get_recent_messages(channel.id, 12)
    summary = await get_summary(channel.id)

    history = "\n".join(
        f"{r['author']}: {r['content']}" for r in recent
    )

    prompt = f"""Channel: #{channel.name}
Channel purpose: {key}

Long-term channel summary:
{summary or "(none yet)"}

Recent conversation:
{history or "(none)"}

User question:
{question}

Answer using the channel context. Do not invent current facts.
If the question asks for current information and no current source/tool
was supplied, say that a live source is needed rather than fabricating it.
"""

    await save_message(channel.id, user.id, str(user), question)

    async with channel.typing():
        answer = await generate_response(system, prompt)

    await save_message(channel.id, bot.user.id, str(bot.user), answer)

    # Keep a compact rolling summary for long-term context.
    if len(recent) >= 10:
        summary_prompt = f"""Summarize this Discord channel conversation into
5-10 concise factual bullets useful for future answers. Preserve learning
goals, unresolved questions, decisions, preferences, and recurring topics.
Do not add facts that are not present.

{history}

Latest answer:
{answer}
"""
        new_summary = await generate_response(
            "You summarize conversation memory accurately and compactly.",
            summary_prompt
        )
        await save_summary(channel.id, new_summary)

    await send_long(channel, answer)


@bot.event
async def on_ready():
    await init_db()
    print(f"Logged in as {bot.user}")
    print(f"Connected to {len(bot.guilds)} server(s)")
    if not scheduler.running:
        scheduler.add_job(post_intel, "cron", hour=8, minute=0)
        scheduler.add_job(post_dsa, "cron", hour=9, minute=0)
        scheduler.add_job(post_learning, "cron", hour=18, minute=0)
        scheduler.add_job(post_anime, "cron", hour=21, minute=0)
        scheduler.start()
        print("Scheduler started:", TIMEZONE)


@bot.command()
async def hello(ctx):
    await ctx.send("Astra is online 🤖")


@bot.command()
async def help_astra(ctx):
    await ctx.send(
        "**Astra commands**\n"
        "`!ask <question>` — channel-aware AI\n"
        "`!intel [topic]` — current RSS intelligence\n"
        "`!learn [topic]` — YouTube learning recommendations\n"
        "`!dsa` — Easy + Medium + Hard DSA set\n"
        "`!anime` — anime image\n"
        "`!memory` — channel memory status\n"
        "You can also mention me naturally."
    )


@bot.command()
async def ask(ctx, *, question):
    await ai_answer(ctx.channel, ctx.author, question)


@bot.command()
async def intel(ctx, *, topic="AI"):
    await post_intel(ctx.channel, topic)


async def post_intel(channel=None, topic="AI"):
    if channel is None:
        channel = bot.get_channel(configured_channel_id(INTEL_CHANNEL_ID))
    if not channel:
        return
    items = await fetch_news(topic)
    text = format_news_for_discord(topic, items)
    await channel.send(text)


@bot.command()
async def learn(ctx, *, topic="agentic AI"):
    await post_learning(ctx.channel, topic)


async def post_learning(channel=None, topic="agentic AI"):
    if channel is None:
        channel = bot.get_channel(configured_channel_id(LEARNING_CHANNEL_ID))
    if not channel:
        return
    videos = await recommend_videos(topic)
    prompt = """You are a technical learning mentor. Given these YouTube
candidates, recommend up to 3 in order of usefulness for an intermediate
AI/ML engineer. Explain prerequisites and what to build after watching.
Do not invent video details.

"""
    for v in videos:
        prompt += f"- {v['title']} | {v['channel']} | {v['url']}\n"
    answer = await generate_response(
        "Recommend learning resources accurately and practically.",
        prompt
    )
    await send_long(channel, f"🎓 **Learning: {topic}**\n\n{answer}")


@bot.command()
async def dsa(ctx):
    await post_dsa(ctx.channel)


async def post_dsa(channel=None):
    if channel is None:
        channel = bot.get_channel(configured_channel_id(DSA_CHANNEL_ID))
    if not channel:
        return
    problems = get_daily_dsa()
    text = "🧠 **Daily DSA — Easy / Medium / Hard**\n\n"
    for p in problems:
        text += (
            f"**{p['difficulty']} — {p['title']}**\n"
            f"{p['url']}\n"
            f"Pattern: {p['pattern']}\n"
            f"Prerequisites: {p['prereq']}\n"
            f"Goal: {p['goal']}\n\n"
        )
    await send_long(channel, text)


@bot.command()
async def anime(ctx):
    await post_anime(ctx.channel)


async def post_anime(channel=None):
    if channel is None:
        channel = bot.get_channel(configured_channel_id(ANIME_CHANNEL_ID))
    if not channel:
        return
    result = await get_anime_image()
    if result:
        embed = discord.Embed(title="🌸 Anime Drop")
        embed.set_image(url=result)
        await channel.send(embed=embed)
    else:
        await channel.send("Could not fetch an anime image right now.")


@bot.command()
async def memory(ctx):
    summary = await get_summary(ctx.channel.id)
    await ctx.send(
        f"**Channel memory**\n"
        f"Messages are stored locally in SQLite.\n"
        f"Summary:\n{summary or '(no summary yet)'}"
    )


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if bot.user not in message.mentions:
        return

    question = message.content
    for mention in message.mentions:
        question = question.replace(f"<@{mention.id}>", "")
        question = question.replace(f"<@!{mention.id}>", "")
    question = question.strip()

    if question:
        try:
            await ai_answer(message.channel, message.author, question)
        except Exception as e:
            print("AI ERROR:", repr(e))
            await message.channel.send(
                "⚠️ AI error. Check that Ollama is running and the model is available."
            )


async def main():
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
