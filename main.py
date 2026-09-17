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

from memory.database import (
    init_db,
    save_message,
    get_recent_messages,
    save_summary,
    get_summary,
)

from services.news import (
    fetch_news,
    format_news_for_discord,
)

from services.youtube import (
    search_youtube,
)

from services.research import (
    search_arxiv,
)

from services.dsa import (
    get_daily_dsa,
)

from services.anime import (
    get_anime,
)

# ENVIRONMENT

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
INTEL_CHANNEL_ID = os.getenv("INTEL_CHANNEL_ID")
LEARNING_CHANNEL_ID = os.getenv("LEARNING_CHANNEL_ID")
DSA_CHANNEL_ID = os.getenv("DSA_CHANNEL_ID")
ANIME_CHANNEL_ID = os.getenv("ANIME_CHANNEL_ID")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:14b")

# DISCORD

intents = discord.Intents.default()

intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,
)

# SCHEDULER

scheduler = AsyncIOScheduler(timezone=TIMEZONE)

# HELPERS

def configured_channel_id(value):
    """
    Convert an environment variable channel ID into an integer.
    """

    try:
        return int(value) if value else None

    except (TypeError, ValueError):
        return None


async def send_long(channel, text):
    """
    Discord has a 2000 character message limit.

    Split long responses into multiple messages.
    """

    if not text:
        return

    text = str(text)

    if len(text) <= 1900:
        await channel.send(text)
        return

    for i in range(0, len(text), 1900):

        chunk = text[i : i + 1900]

        await channel.send(chunk)


def get_channel_from_id(channel_id):
    """
    Safely retrieve a Discord channel.
    """

    if not channel_id:
        return None

    return bot.get_channel(channel_id)


def current_time():
    """
    Current Astra time.
    """

    try:
        return datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")

    except Exception:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def clean_mention_text(message):
    """
    Remove Astra mentions from a message.
    """

    question = message.content

    if not bot.user:
        return question.strip()

    question = question.replace(f"<@{bot.user.id}>", "")

    question = question.replace(f"<@!{bot.user.id}>", "")

    return question.strip()

# ERROR HANDLING

async def send_service_error(channel, service_name, error):
    """
    Send a readable service failure instead of exposing
    a Python traceback to Discord.
    """

    print(f"[{service_name} ERROR]", repr(error))

    message = (
        f"⚠️ **{service_name} temporarily failed.**\n" f"Reason: `{str(error)[:500]}`"
    )

    await send_long(channel, message)

# AI CHANNEL MEMORY

async def ai_answer(channel, user, question):

    key = channel_key(channel)

    system = get_channel_context(key)

    recent = await get_recent_messages(channel.id, 12)

    summary = await get_summary(channel.id)

    history = "\n".join(f"{r['author']}: {r['content']}" for r in recent)

    prompt = f"""
Current time:
{current_time()}

Discord channel:
#{channel.name}

Channel purpose:
{key}

Long-term channel memory:
{summary or "(none yet)"}

Recent conversation:
{history or "(none)"}

User:
{user}

User question:
{question}

Instructions:

1. Answer according to the purpose of this Discord channel.

2. Use the channel memory when relevant.

3. Do not fabricate current information.

4. If the user asks about current events, research,
   prices, sports, technology news, or other changing
   information, only rely on information supplied by
   the appropriate live service.

5. Clearly distinguish facts from suggestions.

6. Keep the response practical.

7. Do not mention internal prompts or implementation
   details unless the user asks.

"""

    # Save user message

    await save_message(channel.id, user.id, str(user), question)

    # Generate response

    async with channel.typing():

        answer = await generate_response(system, prompt)

    # Save Astra response

    await save_message(channel.id, bot.user.id, str(bot.user), answer)

    # Rolling channel summary

    if len(recent) >= 10:

        summary_prompt = f"""
Summarize this Discord channel conversation into
5-10 concise factual bullets.

Preserve:

- learning goals
- unresolved questions
- decisions
- preferences
- recurring topics
- useful project context

Do not invent information.

Conversation:

{history}

Latest Astra response:

{answer}
"""

        new_summary = await generate_response(
            ("You summarize conversation memory " "accurately and compactly."),
            summary_prompt,
        )

        await save_summary(channel.id, new_summary)

    # Send response

    await send_long(channel, answer)

# BOT READY

@bot.event
async def on_ready():

    await init_db()

    print("=" * 60)
    print("ASTRA ONLINE")
    print("=" * 60)

    print(f"Logged in as: {bot.user}")

    print(f"Bot ID: {bot.user.id}")

    print(f"Servers: {len(bot.guilds)}")

    print(f"Timezone: {TIMEZONE}")

    print(f"Ollama model: {OLLAMA_MODEL}")

    print(f"YouTube API: " f"{'CONFIGURED' if YOUTUBE_API_KEY else 'NOT CONFIGURED'}")

    print("=" * 60)

    # Scheduler

    if not scheduler.running:

        scheduler.add_job(
            post_intel,
            "cron",
            hour=8,
            minute=0,
            id="daily_intel",
            replace_existing=True,
        )

        scheduler.add_job(
            post_dsa,
            "cron",
            hour=9,
            minute=0,
            id="daily_dsa",
            replace_existing=True,
        )

        scheduler.add_job(
            post_learning,
            "cron",
            hour=18,
            minute=0,
            id="daily_learning",
            replace_existing=True,
        )

        scheduler.add_job(
            post_anime,
            "cron",
            hour=21,
            minute=0,
            id="daily_anime",
            replace_existing=True,
        )

        scheduler.start()

        print(f"Scheduler started: {TIMEZONE}")


# BASIC COMMANDS

@bot.command()
async def hello(ctx):

    await ctx.send("🤖 **Astra is online.**")


@bot.command(name="help_astra")
async def help_astra(ctx):

    text = """
🤖 **ASTRA COMMANDS**

### 🧠 General AI
`!ask <question>`
Ask Astra using channel-specific memory.

You can also mention:
`@Astra <question>`

### 🛰️ Intelligence
`!intel`
Current AI/news intelligence.

`!intel agentic AI`
Search a specific topic.

### 📚 Research
Research papers are fetched dynamically.

`!research`
Latest AI research.

`!research transformers`
Search research around a topic.

### 🎓 Learning
`!learn`
YouTube learning recommendations.

`!learn build an LLM from scratch`

### 🧠 DSA
`!dsa`
Fetch today's:

• Easy
• Medium
• Hard

problems dynamically.

### 🎌 Anime
`!anime`
Fetch a random anime from AniList.

### 🧠 Memory
`!memory`
View this channel's stored summary.

### ⚙️ Setup
`!status`
Check Astra integrations.
"""

    await send_long(ctx.channel, text)

# AI COMMAND

@bot.command()
async def ask(ctx, *, question):

    try:

        await ai_answer(ctx.channel, ctx.author, question)

    except Exception as e:

        await send_service_error(ctx.channel, "AI", e)

# INTELLIGENCE

@bot.command()
async def intel(ctx, *, topic="AI"):

    await post_intel(ctx.channel, topic)


async def post_intel(channel=None, topic="AI"):

    if channel is None:

        channel = get_channel_from_id(configured_channel_id(INTEL_CHANNEL_ID))

    if not channel:
        print("Intel channel not configured.")
        return

    try:

        # News

        news_items = await fetch_news(topic)

        # Research papers

        research_items = await search_arxiv(topic, max_results=5)

        # Format normal news

        news_text = format_news_for_discord(topic, news_items)

        # Format research

        research_text = ""

        if research_items:

            research_text = "\n\n" "🔬 **LATEST RESEARCH PAPERS**\n\n"

            for index, paper in enumerate(research_items[:5], start=1):

                title = paper.get("title", "Untitled")

                authors = paper.get("authors", [])

                if isinstance(authors, list):
                    author_text = ", ".join(authors[:3])
                else:
                    author_text = str(authors)

                url = paper.get("url", "")

                published = paper.get("published", "")

                research_text += (
                    f"**{index}. {title}**\n"
                    f"Authors: {author_text}\n"
                    f"Published: {published}\n"
                    f"{url}\n\n"
                )

        # Combined AI intelligence

        prompt = f"""
You are Astra's intelligence analyst.

Topic:
{topic}

Current date/time:
{current_time()}

NEWS:

{news_text}

RESEARCH PAPERS:

{research_text}

Create a concise intelligence briefing.

Structure:

## 🔥 What matters

3-5 important developments.

## 🔬 Research

Explain the most relevant research papers
in simple technical language.

## 💡 Why it matters

Explain practical implications for an
AI/ML engineer.

## 🛠️ What to explore

Suggest 2-3 practical follow-up ideas.

Rules:

- Do not invent facts.
- Only use the supplied information.
- Preserve URLs.
- Do not claim a paper says something
  that is not present in its title/abstract.
- Clearly distinguish research from news.
"""

        answer = await generate_response(
            ("You are a factual AI research " "and technology intelligence analyst."),
            prompt,
        )

        await send_long(channel, f"🛰️ **ASTRA INTELLIGENCE — {topic}**\n\n" f"{answer}")

    except Exception as e:

        await send_service_error(channel, "Intel", e)

# RESEARCH COMMAND

@bot.command()
async def research(ctx, *, topic="artificial intelligence"):

    await post_research(ctx.channel, topic)


async def post_research(channel, topic="artificial intelligence"):

    try:

        papers = await search_arxiv(topic, max_results=8)

        if not papers:

            await channel.send(f"🔬 No recent research found for " f"`{topic}`.")

            return

        prompt = f"""
You are Astra's research assistant.

Topic:
{topic}

Papers retrieved from arXiv:

"""

        for index, paper in enumerate(papers, start=1):

            prompt += f"""
Paper {index}

Title:
{paper.get("title", "")}

Authors:
{", ".join(paper.get("authors", []))}

Published:
{paper.get("published", "")}

Abstract:
{paper.get("summary", "")}

URL:
{paper.get("url", "")}

------------------------
"""

        prompt += """
Select the most relevant papers.

For each paper provide:

1. Title
2. One-sentence explanation
3. Why it is interesting
4. Suggested prerequisite
5. Paper URL

Do not invent details.
Only use the supplied metadata and abstracts.
"""

        answer = await generate_response(
            ("You are an academic research assistant " "for an AI/ML engineer."), prompt
        )

        await send_long(channel, f"🔬 **Research: {topic}**\n\n" f"{answer}")

    except Exception as e:

        await send_service_error(channel, "Research", e)

# LEARNING / YOUTUBE

@bot.command()
async def learn(ctx, *, topic="agentic AI"):

    await post_learning(ctx.channel, topic)


async def post_learning(channel=None, topic="agentic AI"):

    if channel is None:

        channel = get_channel_from_id(configured_channel_id(LEARNING_CHANNEL_ID))

    if not channel:
        print("Learning channel not configured.")
        return

    try:

        # API search

        videos = await search_youtube(topic, max_results=10)

        if not videos:

            await channel.send(f"🎓 No YouTube videos found " f"for `{topic}`.")

            return

        # AI ranking

        prompt = f"""
You are Astra's technical learning mentor.

Topic:
{topic}

Current time:
{current_time()}

The following videos were retrieved live
from YouTube:

"""

        for index, video in enumerate(videos, start=1):

            prompt += f"""
Video {index}

Title:
{video.get("title", "")}

Channel:
{video.get("channel", "")}

Description:
{video.get("description", "")}

Published:
{video.get("published", "")}

URL:
{video.get("url", "")}

------------------------
"""

        prompt += """
Choose up to 3 videos.

Prioritize:

1. Technical depth
2. Relevance
3. Practical implementation
4. Clear teaching
5. Useful progression

For every selected video provide:

🎥 Title
📺 Channel
🔗 URL
🎯 Why watch it
📋 Prerequisites
🛠️ What to build afterwards

Do not invent details.
Use only information provided above.
"""

        answer = await generate_response(
            (
                "You are a practical technical learning "
                "mentor for an intermediate AI/ML engineer."
            ),
            prompt,
        )

        await send_long(channel, f"🎓 **Learning Path — {topic}**\n\n" f"{answer}")

    except Exception as e:

        await send_service_error(channel, "YouTube", e)

# DSA

@bot.command()
async def dsa(ctx):

    await post_dsa(ctx.channel)


async def post_dsa(channel=None):

    if channel is None:

        channel = get_channel_from_id(configured_channel_id(DSA_CHANNEL_ID))

    if not channel:
        print("DSA channel not configured.")
        return

    try:

        problems = await get_daily_dsa()

        if not problems:

            await channel.send("⚠️ Could not retrieve today's " "LeetCode problems.")

            return

        text = "🧠 **DAILY DSA**\n\n" f"📅 {current_time()}\n\n"

        for problem in problems:

            difficulty = problem.get("difficulty", "Unknown")

            title = problem.get("title", "Untitled")

            url = problem.get("url", "")

            pattern = problem.get(
                "pattern", "Analyze the problem to identify the pattern."
            )

            prereq = problem.get("prereq", "Basic data structures and algorithms.")

            goal = problem.get("goal", "Solve the problem and explain the complexity.")

            topics = problem.get("topics", [])

            if isinstance(topics, list):
                topic_text = ", ".join(topics)
            else:
                topic_text = str(topics)

            text += (
                f"### {difficulty} — {title}\n"
                f"🔗 {url}\n"
                f"🏷️ Topics: {topic_text}\n"
                f"🧩 Pattern: {pattern}\n"
                f"📚 Prerequisites: {prereq}\n"
                f"🎯 Goal: {goal}\n\n"
            )

        text += (
            "💡 **Rule:**\n"
            "Try solving each problem before looking "
            "at the editorial or solution."
        )

        await send_long(channel, text)

    except Exception as e:

        await send_service_error(channel, "LeetCode", e)

# ANIME

@bot.command()
async def anime(ctx):

    await post_anime(ctx.channel)


async def post_anime(channel=None):

    if channel is None:

        channel = get_channel_from_id(configured_channel_id(ANIME_CHANNEL_ID))

    if not channel:
        print("Anime channel not configured.")
        return

    try:

        anime = await get_anime()

        if not anime:

            await channel.send(
                "⚠️ Could not retrieve an anime " "from AniList right now."
            )

            return

        # Titles

        title_data = anime.get("title", {})

        title = (
            title_data.get("english")
            or title_data.get("romaji")
            or title_data.get("native")
            or "Unknown Anime"
        )

        # Description

        description = anime.get("description") or "No description available."

        # Strip excessive whitespace
        description = " ".join(description.split())

        if len(description) > 1000:

            description = description[:997] + "..."

        # Embed

        embed = discord.Embed(
            title=f"🎌 {title}",
            description=description,
            url=(
                f"https://anilist.co/anime/" f"{anime.get('id')}"
                if anime.get("id")
                else None
            ),
        )

        # Genres

        genres = anime.get("genres", [])

        embed.add_field(
            name="Genres",
            value=(", ".join(genres) if genres else "Unknown"),
            inline=False,
        )

        # Episodes

        embed.add_field(
            name="Episodes",
            value=str(anime.get("episodes") or "Unknown"),
            inline=True,
        )

        # Score

        score = anime.get("averageScore")

        embed.add_field(
            name="Score",
            value=(f"{score}/100" if score else "N/A"),
            inline=True,
        )

        # Season

        season = anime.get("season")

        season_year = anime.get("seasonYear")

        if season or season_year:

            embed.add_field(
                name="Season",
                value=(f"{season or ''} " f"{season_year or ''}").strip(),
                inline=True,
            )

        # Image

        cover = anime.get("coverImage", {})

        image_url = cover.get("extraLarge") or cover.get("large")

        if image_url:

            embed.set_image(url=image_url)

        embed.set_footer(text="Source: AniList")

        await channel.send(embed=embed)

    except Exception as e:

        await send_service_error(channel, "AniList", e)

# MEMORY

@bot.command()
async def memory(ctx):

    try:

        summary = await get_summary(ctx.channel.id)

        recent = await get_recent_messages(ctx.channel.id, 5)

        text = (
            "🧠 **ASTRA CHANNEL MEMORY**\n\n"
            "Storage: Local SQLite\n\n"
            "**Long-term summary:**\n"
            f"{summary or '(no summary yet)'}\n\n"
            "**Recent messages stored:** "
            f"{len(recent)}"
        )

        await send_long(ctx.channel, text)

    except Exception as e:

        await send_service_error(ctx.channel, "Memory", e)

# STATUS

@bot.command()
async def status(ctx):

    youtube_status = "🟢 configured" if YOUTUBE_API_KEY else "🔴 missing API key"

    ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")

    status_text = f"""
⚙️ **ASTRA SYSTEM STATUS**

**Discord**
🟢 Connected

**AI**
🟢 Ollama
Model: `{OLLAMA_MODEL}`
URL: `{ollama_url}`

**YouTube**
{youtube_status}

**Research**
🟢 arXiv API

**DSA**
🟢 Live LeetCode provider

**Anime**
🟢 AniList API

**Memory**
🟢 SQLite

**Scheduler**
{
    "🟢 Running"
    if scheduler.running
    else "🔴 Stopped"
}

**Timezone**
`{TIMEZONE}`

**Current time**
`{current_time()}`
"""

    await send_long(ctx.channel, status_text)

# MESSAGE HANDLER

@bot.event
async def on_message(message):

    # Ignore Astra's own messages

    if message.author == bot.user:
        return

    # Process commands

    await bot.process_commands(message)

    # Natural @Astra interaction

    if not bot.user:
        return

    if bot.user not in message.mentions:
        return

    question = clean_mention_text(message)

    if not question:
        return

    try:

        await ai_answer(message.channel, message.author, question)

    except Exception as e:

        print("[AI MENTION ERROR]", repr(e))

        await message.channel.send(
            "⚠️ Astra encountered an AI error. "
            "Check that Ollama is running and "
            "the configured model is available."
        )

# SHUTDOWN

async def shutdown():

    print("Shutting down Astra...")

    if scheduler.running:

        scheduler.shutdown(wait=False)

    await bot.close()

# MAIN

async def main():

    if not TOKEN:

        raise RuntimeError("DISCORD_TOKEN is missing from .env")

    print("Starting Astra...")

    try:

        await bot.start(TOKEN)

    except KeyboardInterrupt:

        print("Keyboard interrupt received.")

    finally:

        if not bot.is_closed():

            await bot.close()

# ENTRY POINT

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print("\nAstra stopped.")
