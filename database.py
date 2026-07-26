import sqlite3

DATABASE_NAME = "messages.db"


def init_db():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                text TEXT,
                media_type TEXT,
                telegram_file_id TEXT,
                date TEXT,
                time TEXT
            )
        """)

        conn.commit()


def save_message(data: dict):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages (
                telegram_id,
                username,
                first_name,
                last_name,
                text,
                media_type,
                telegram_file_id,
                date,
                time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["telegram_id"],
            data["username"],
            data["first_name"],
            data["last_name"],
            data["text"],
            data["media_type"],
            data["telegram_file_id"],
            data["date"],
            data["time"]
        ))

        conn.commit()


def get_stats():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(DISTINCT telegram_id) FROM messages")
        users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM messages")
        messages = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM messages WHERE media_type='photo'")
        photos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM messages WHERE media_type='video'")
        videos = cursor.fetchone()[0]

    return {
        "users": users,
        "messages": messages,
        "photos": photos,
        "videos": videos
    }