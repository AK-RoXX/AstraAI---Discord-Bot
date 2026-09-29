# 🤖 Astra — AI-Powered Discord Work Automation Bot

> **Astra is a personal AI automation assistant that turns Discord into an intelligent workspace for research, learning, DSA practice, news, and entertainment.**

Astra combines **LLMs, live APIs, channel-specific context, persistent memory, scheduled automation, and Discord interactions** into a single personal AI workspace.

Instead of having one generic chatbot, Astra gives every Discord channel a specific purpose and context.

---

## ✨ Features

### 🛰️ `#intel` — AI Intelligence

Astra continuously gathers information from multiple live sources:

* 🔬 Latest AI/ML research papers
* 🤖 AI technology news
* 📰 Technology developments
* 🏀 Sports news
* 💰 Finance-related news
* 📊 Topic-specific intelligence

Research papers are retrieved dynamically from **arXiv**, while news is retrieved from configured RSS sources.

Example:

```text
!intel
```

or:

```text
!intel agentic AI
```

Astra then uses the LLM to turn the retrieved information into a concise intelligence briefing.

---

### 🔬 `#research` — Research Assistant

Search recent AI/ML research directly from Discord.

```text
!research agentic AI
```

```text
!research multimodal RAG
```

```text
!research computer vision
```

Astra retrieves papers dynamically and provides:

* Paper title
* Authors
* Publication date
* Abstract
* Relevance
* Prerequisites
* Practical implications
* Paper URL

No research-paper list is hardcoded into the application.

---

### 🎓 `#learning` — AI Learning Mentor

Astra searches YouTube for learning resources using the **YouTube Data API**.

Example:

```text
!learn build an LLM from scratch
```

```text
!learn LangGraph agents
```

```text
!learn transformers from scratch
```

The LLM analyzes the retrieved videos and recommends the most useful resources based on:

* Technical depth
* Relevance
* Practical value
* Prerequisites
* Learning progression

It can also suggest what to build after watching the videos.

---

### 🧠 `#dsa` — Daily LeetCode Practice

Every day Astra retrieves a fresh:

* 🟢 Easy
* 🟡 Medium
* 🔴 Hard

problem set.

Example:

```text
!dsa
```

Each problem contains:

* Title
* Difficulty
* LeetCode URL
* Topic
* Pattern
* Prerequisites
* Learning goal

The problems are retrieved dynamically rather than stored as a static list.

This allows Astra to eventually support:

* Problem history
* Weak-topic detection
* Difficulty progression
* Personalized recommendations
* Spaced repetition
* Performance tracking

---

### 🎌 `#anime` — Anime Discovery

Astra retrieves anime dynamically using **AniList**.

```text
!anime
```

The Discord embed contains:

* Anime title
* Cover image
* Description
* Genres
* Episodes
* Score
* Season
* AniList page

The application does not store a static anime image collection.

---

## 🧠 Channel-Aware AI

Astra is not just a generic chatbot.

Each channel has its own context.

```text
Discord
   │
   ▼
┌──────────────────────┐
│       Astra AI       │
└──────────┬───────────┘
           │
     Channel Context
           │
 ┌─────────┼─────────┐
 ▼         ▼         ▼
Intel   Learning    DSA
 │         │         │
 ▼         ▼         ▼
Research YouTube  LeetCode

           │
           ▼
        Anime
           │
           ▼
       AniList
```

For example, asking:

```text
@Astra explain RAG
```

inside `#research` produces a research-oriented response.

The same question inside `#learning` can produce a learning-oriented explanation and implementation roadmap.

---

# 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │      Discord        │
                         │      Server         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       Astra         │
                         │   Discord Bot       │
                         └──────────┬──────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
       Channel Context          Commands              Scheduler
             │                      │                      │
             │                      │                      │
             ▼                      ▼                      ▼
       ┌───────────┐        ┌───────────────┐       APScheduler
       │ AI Context│        │ Service Layer │
       └─────┬─────┘        └───────┬───────┘
             │                      │
             │        ┌─────────────┼──────────────┐
             │        │             │              │
             │        ▼             ▼              ▼
             │     YouTube       arXiv        LeetCode
             │
             │        ┌─────────────┐
             │        │   AniList   │
             │        └─────────────┘
             │
             ▼
       ┌───────────────┐
       │ Ollama / LLM  │
       └───────┬───────┘
               │
               ▼
       ┌───────────────┐
       │ SQLite Memory │
       └───────────────┘
```

---

# 📁 Project Structure

```text
astra-discord/
│
├── main.py
├── README.md
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
│
├── ai/
│   ├── __init__.py
│   ├── llm.py
│   └── context.py
│
├── memory/
│   ├── __init__.py
│   └── database.py
│
├── services/
│   ├── __init__.py
│   ├── news.py
│   ├── youtube.py
│   ├── research.py
│   ├── dsa.py
│   └── anime.py
│
└── data/
    └── astra.db
```

---

# 🧩 Technology Stack

| Component     | Technology          |
| ------------- | ------------------- |
| Language      | Python              |
| Discord       | `discord.py`        |
| AI            | Ollama              |
| Default LLM   | Qwen                |
| Memory        | SQLite              |
| HTTP          | HTTPX               |
| Scheduling    | APScheduler         |
| Research      | arXiv API           |
| Learning      | YouTube Data API    |
| DSA           | LeetCode provider   |
| Anime         | AniList GraphQL API |
| News          | RSS                 |
| Configuration | python-dotenv       |

---

# 🤖 AI Layer

Astra currently uses **Ollama** for local inference.

Default configuration:

```env
LLM_PROVIDER=ollama
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5-coder:14b
```

You can change the model:

```env
OLLAMA_MODEL=qwen3-coder:30b
```

or another model available locally through Ollama.

Check installed models:

```bash
ollama list
```

Run a model manually:

```bash
ollama run qwen2.5-coder:14b
```

Astra communicates with Ollama through its HTTP API.

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

```env
# ==========================================================
# DISCORD
# ==========================================================

DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN


# ==========================================================
# AI
# ==========================================================

LLM_PROVIDER=ollama

OLLAMA_URL=http://127.0.0.1:11434

OLLAMA_MODEL=qwen2.5-coder:14b


# ==========================================================
# YOUTUBE
# ==========================================================

YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY


# ==========================================================
# DISCORD CHANNELS
# ==========================================================

INTEL_CHANNEL_ID=YOUR_INTEL_CHANNEL_ID

LEARNING_CHANNEL_ID=YOUR_LEARNING_CHANNEL_ID

DSA_CHANNEL_ID=YOUR_DSA_CHANNEL_ID

ANIME_CHANNEL_ID=YOUR_ANIME_CHANNEL_ID


# ==========================================================
# TIMEZONE
# ==========================================================

TIMEZONE=Asia/Kolkata
```

Never commit `.env` to Git.

---

# 🔐 Discord Bot Setup

## 1. Create a Discord Application

Go to the Discord Developer Portal and create a new application.

Create a bot under:

```text
Application
   └── Bot
```

Copy the bot token.

Put it in:

```env
DISCORD_TOKEN=...
```

---

## 2. Enable Message Content Intent

In the Discord Developer Portal:

```text
Bot
└── Privileged Gateway Intents
    └── Message Content Intent
```

Enable it.

This is required because Astra needs to read messages and respond to mentions.

---

## 3. Invite Astra

Generate an OAuth2 installation URL with the required permissions.

At minimum Astra needs permission to:

* View channels
* Send messages
* Embed links
* Read message history

---

# ▶️ Installation

Clone the project:

```bash
git clone <your-repository-url>
cd astra-discord
```

Create a virtual environment:

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

# 🧠 Install Ollama

Install Ollama and verify:

```bash
ollama --version
```

Download the model:

```bash
ollama pull qwen2.5-coder:14b
```

Test it:

```bash
ollama run qwen2.5-coder:14b
```

Keep Ollama running while Astra is running.

---

# ▶️ Run Astra

Start the bot:

```powershell
python main.py
```

Expected output:

```text
============================================================
ASTRA ONLINE
============================================================
Logged in as: Astra#0000
Servers: 1
Timezone: Asia/Kolkata
Ollama model: qwen2.5-coder:14b
YouTube API: CONFIGURED
============================================================
Scheduler started: Asia/Kolkata
```

---

# 📺 YouTube API Setup

Astra uses the YouTube Data API for live learning-resource discovery.

The application requires:

```env
YOUTUBE_API_KEY=...
```

Create a Google Cloud project and enable:

```text
YouTube Data API v3
```

Then create an API key and place it inside `.env`.

Verify:

```text
!status
```

You should see:

```text
YouTube
🟢 configured
```

If the key is missing:

```text
YouTube
🔴 missing API key
```

---

# 🔬 Research API

Research discovery uses the arXiv API.

No hardcoded paper list is used.

A query such as:

```text
!research agentic AI
```

is translated into a live arXiv search.

The returned metadata can include:

```text
Title
Authors
Abstract
Published
Updated
URL
```

Astra then uses the LLM to organize the results.

---

# 🧠 DSA API

The DSA system is designed around a dynamic LeetCode provider.

The important architectural principle is:

```text
Discord
   ↓
DSA Service
   ↓
LeetCode API/provider
   ↓
Problem metadata
   ↓
Astra LLM
   ↓
Pattern + prerequisites + goal
```

There is intentionally **no hardcoded problem database** in `main.py`.

This makes it possible to replace the provider later without changing the Discord bot.

Potential future improvements include:

* LeetCode history tracking
* User-specific solved status
* Topic weakness analysis
* Difficulty adaptation
* Daily streaks
* Spaced repetition
* Contest preparation

---

# 🎌 Anime API

Anime discovery uses AniList.

Astra dynamically retrieves anime metadata including:

```text
title
description
cover image
genres
episodes
score
season
year
```

The Discord response is rendered as an embed.

Example:

```text
🎌 Frieren: Beyond Journey's End

Genres:
Adventure, Drama, Fantasy

Episodes:
28

Score:
92/100
```

---

# ⏰ Automation

Astra uses APScheduler to automatically publish content.

Default schedule:

| Time  | Channel     | Task                  |
| ----- | ----------- | --------------------- |
| 08:00 | `#intel`    | Intelligence briefing |
| 09:00 | `#dsa`      | Daily DSA             |
| 18:00 | `#learning` | Learning resources    |
| 21:00 | `#anime`    | Anime discovery       |

Timezone:

```env
TIMEZONE=Asia/Kolkata
```

The schedule can be changed directly in `main.py`.

For example:

```python
scheduler.add_job(
    post_dsa,
    "cron",
    hour=10,
    minute=30,
)
```

---

# 💬 Commands

## General

```text
!hello
```

Check whether Astra is online.

```text
!help_astra
```

Display available commands.

---

## AI

```text
!ask <question>
```

Example:

```text
!ask explain MCP servers
```

Astra uses:

* Channel context
* Recent conversation
* Persistent memory
* Local LLM

---

## Intelligence

```text
!intel
```

Default AI intelligence.

```text
!intel agentic AI
```

Topic-specific intelligence.

---

## Research

```text
!research agentic AI
```

```text
!research RAG
```

```text
!research computer vision
```

---

## Learning

```text
!learn agentic AI
```

```text
!learn build an LLM from scratch
```

```text
!learn LangGraph
```

---

## DSA

```text
!dsa
```

Retrieves:

```text
Easy
Medium
Hard
```

---

## Anime

```text
!anime
```

Retrieves an anime dynamically.

---

## Memory

```text
!memory
```

Displays the current channel's stored memory summary.

---

## Status

```text
!status
```

Displays the state of Astra's integrations.

Example:

```text
Discord
🟢 Connected

AI
🟢 Ollama

YouTube
🟢 configured

Research
🟢 arXiv API

DSA
🟢 Live provider

Anime
🟢 AniList API

Memory
🟢 SQLite

Scheduler
🟢 Running
```

---

# 🧠 Persistent Memory

Astra stores conversation data locally using SQLite.

The memory layer maintains:

```text
messages
channel_summaries
```

Recent messages are provided to the LLM for contextual responses.

When enough messages accumulate, Astra generates a compact summary.

Example:

```text
User is currently learning agentic AI.

User prefers practical implementations.

Current project involves LangGraph and MCP.

User is interested in production-oriented
multi-agent systems.
```

This allows the conversation to remain useful without continuously sending the entire channel history to the model.

---

# 🔒 Privacy

Astra is designed to keep AI processing local where possible.

The default AI architecture is:

```text
Discord
   ↓
Astra
   ↓
Local Ollama
   ↓
Local SQLite
```

External APIs are used only for services that require live external information, such as:

* YouTube
* arXiv
* LeetCode provider
* AniList
* News feeds

Do not put secrets, API keys, or tokens inside source code.

---

# 🧱 Service Architecture

Each external integration is isolated inside `services/`.

### `services/news.py`

Responsible for:

```text
RSS
 ↓
News items
 ↓
Formatting
```

### `services/research.py`

Responsible for:

```text
Topic
 ↓
arXiv API
 ↓
Research metadata
```

### `services/youtube.py`

Responsible for:

```text
Topic
 ↓
YouTube Data API
 ↓
Video metadata
```

### `services/dsa.py`

Responsible for:

```text
Daily selection
 ↓
LeetCode provider
 ↓
Problem metadata
 ↓
AI-generated learning information
```

### `services/anime.py`

Responsible for:

```text
AniList GraphQL
 ↓
Anime metadata
 ↓
Discord embed
```

This separation makes it easy to replace APIs without rewriting the Discord bot.

---

# 🧪 Development Philosophy

Astra follows several principles:

### 1. Don't hardcode dynamic information

Bad:

```python
PROBLEMS = [
    "Two Sum",
    "LRU Cache",
    "Merge Sort"
]
```

Good:

```text
Discord
↓
Live API
↓
Problem selection
↓
LLM enrichment
```

---

### 2. Keep integrations modular

External APIs should never be deeply embedded inside `main.py`.

Instead:

```text
main.py
   ↓
services/
   ↓
external API
```

---

### 3. LLMs should enrich data, not fabricate it

For current information:

```text
API
 ↓
Verified metadata
 ↓
LLM
 ↓
Explanation
```

not:

```text
LLM
 ↓
Guess current information
```

---

### 4. Channel context matters

Astra should behave differently depending on where it is being used.

```text
#intel
→ current intelligence

#research
→ academic research

#learning
→ educational resources

#dsa
→ algorithm practice

#anime
→ anime discovery
```

---

# 🚀 Future Roadmap

## Phase 1 — Core Bot

* [x] Discord bot
* [x] Commands
* [x] Ollama integration
* [x] SQLite memory
* [x] Channel-aware AI
* [x] Scheduled tasks

---

## Phase 2 — Live Data

* [x] News feeds
* [x] arXiv research
* [x] YouTube API
* [x] AniList
* [x] Dynamic DSA provider

---

## Phase 3 — Personalization

Planned:

```text
User
 ↓
Activity history
 ↓
Knowledge graph
 ↓
Weakness detection
 ↓
Personalized recommendations
```

Potential features:

* Personalized DSA difficulty
* Learning progress tracking
* Research interests
* Topic embeddings
* Long-term user profile
* Skill graph

---

## Phase 4 — Agentic Astra

Transform Astra from a chatbot into an agentic system.

```text
                    ┌─────────────┐
                    │    Astra    │
                    │ Orchestrator│
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
     Research Agent   Learning Agent    DSA Agent
          │                │                │
          ▼                ▼                ▼
        arXiv           YouTube         LeetCode
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                     Memory Agent
                           │
                           ▼
                       SQLite
```

Future agents could include:

* Research Agent
* News Agent
* Learning Agent
* DSA Agent
* Finance Agent
* Sports Agent
* Memory Agent
* Planning Agent
* Notification Agent

---

# 🔮 Advanced Features

### MCP Integration

Astra can eventually expose tools through MCP:

```text
Astra
 │
 ├── arXiv MCP
 ├── YouTube MCP
 ├── GitHub MCP
 ├── Notion MCP
 ├── LeetCode MCP
 └── Calendar MCP
```

This would allow Astra to perform actions rather than simply answer questions.

---

### Autonomous Daily Planning

Eventually:

```text
08:00
↓
Astra checks goals
↓
Research discovered
↓
Learning resource found
↓
DSA weakness detected
↓
Daily plan generated
↓
Discord notification
```

Example:

```text
🌅 Good morning Ankit.

Today's AI learning plan:

09:00
→ Solve Binary Search problem

10:00
→ Read latest Agentic AI paper

14:00
→ Implement tool calling

18:00
→ Watch LangGraph tutorial

21:00
→ Review today's DSA mistakes
```

---

# 🛠️ Troubleshooting

## Astra does not respond

Check:

```text
Message Content Intent
```

in the Discord Developer Portal.

Also verify:

```env
DISCORD_TOKEN=...
```

---

## Ollama error

Check:

```bash
ollama list
```

Then:

```bash
ollama run qwen2.5-coder:14b
```

Verify:

```env
OLLAMA_URL=http://127.0.0.1:11434
```

---

## YouTube does not work

Run:

```text
!status
```

If you see:

```text
YouTube
🔴 missing API key
```

configure:

```env
YOUTUBE_API_KEY=...
```

Make sure the YouTube Data API is enabled in Google Cloud.

---

## Research does not work

Check your internet connection and try:

```text
!research artificial intelligence
```

The research service depends on the arXiv API.

---

## DSA does not work

The DSA provider is intentionally API-driven.

Check the error printed in the terminal.

Do **not** replace it with a hardcoded problem list.

---

## Anime does not work

Try:

```text
!anime
```

and inspect the terminal output.

The anime service depends on AniList.

---

# 📊 Why Astra?

Most Discord bots are built around:

```text
Command → Response
```

Astra is designed around:

```text
Context
   +
Memory
   +
Live Data
   +
LLM
   +
Automation
   =
Personal AI Workspace
```

The goal is not simply to build another Discord chatbot.

The goal is to build an **AI operating layer for personal technical work**.

---

# 🏆 Project Highlights

Astra demonstrates practical implementation of:

* LLM integration
* Local AI inference
* AI agents
* API orchestration
* Discord automation
* Persistent memory
* Retrieval from live sources
* Scheduled autonomous tasks
* Channel-specific context
* Structured prompting
* External API integration
* Async Python
* SQLite persistence
* AI-assisted information synthesis

---