import aiosqlite
from config import DB_NAME

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                user_id INTEGER PRIMARY KEY,
                default_format TEXT DEFAULT 'PNG',
                auto_preview INTEGER DEFAULT 1,
                track_history INTEGER DEFAULT 1
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                url TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER,
                url TEXT,
                PRIMARY KEY (user_id, url)
            )
        ''')
        await db.commit()

async def get_settings(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT default_format, auto_preview, track_history FROM settings WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"default_format": row[0], "auto_preview": bool(row[1]), "track_history": bool(row[2])}
            await db.execute("INSERT INTO settings (user_id) VALUES (?)", (user_id,))
            await db.commit()
            return {"default_format": "PNG", "auto_preview": True, "track_history": True}

async def update_setting(user_id: int, column: str, value):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f"UPDATE settings SET {column} = ? WHERE user_id = ?", (value, user_id))
        await db.commit()

async def add_history(user_id: int, url: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO history (user_id, url) VALUES (?, ?)", (user_id, url))
        await db.commit()

async def get_history(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT url FROM history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", (user_id,)) as cursor:
            return [row[0] for row in await cursor.fetchall()]

async def add_favorite(user_id: int, url: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO favorites (user_id, url) VALUES (?, ?)", (user_id, url))
        await db.commit()

async def get_favorites(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT url FROM favorites WHERE user_id = ?", (user_id,)) as cursor:
            return [row[0] for row in await cursor.fetchall()]

