from pathlib import Path
import aiosqlite

DB_PATH = Path("data/astra.db")
DB_PATH.parent.mkdir(exist_ok=True)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS channel_summaries (
            channel_id INTEGER PRIMARY KEY,
            summary TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        await db.commit()


async def save_message(channel_id, user_id, author, content):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages(channel_id,user_id,author,content) VALUES(?,?,?,?)",
            (channel_id, user_id, author, content)
        )
        await db.commit()


async def get_recent_messages(channel_id, limit=12):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT author, content, created_at
               FROM messages WHERE channel_id=?
               ORDER BY id DESC LIMIT ?""",
            (channel_id, limit)
        )
        rows = await cursor.fetchall()
        return list(reversed(rows))


async def save_summary(channel_id, summary):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO channel_summaries(channel_id,summary)
               VALUES(?,?)
               ON CONFLICT(channel_id) DO UPDATE SET
               summary=excluded.summary,
               updated_at=CURRENT_TIMESTAMP""",
            (channel_id, summary)
        )
        await db.commit()


async def get_summary(channel_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT summary FROM channel_summaries WHERE channel_id=?",
            (channel_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else ""
