import os
import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE_PATH = "hotpuppy.db"


def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create images table to track evolution
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_url TEXT NOT NULL,
            prompt TEXT NOT NULL,
            user_input TEXT,
            is_seed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def add_image(image_url: str, prompt: str, user_input: str = None, is_seed: bool = False):
    """Add a new image to the evolution chain"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO images (image_url, prompt, user_input, is_seed, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (image_url, prompt, user_input, is_seed, datetime.now().isoformat()))

    conn.commit()
    image_id = cursor.lastrowid
    conn.close()
    return image_id


def get_latest_image():
    """Get the most recent image in the evolution chain"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, image_url, prompt, user_input, is_seed, created_at
        FROM images
        ORDER BY id DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "id": result[0],
            "image_url": result[1],
            "prompt": result[2],
            "user_input": result[3],
            "is_seed": bool(result[4]),
            "created_at": result[5]
        }
    return None


def get_all_images():
    """Get all images in chronological order"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, image_url, prompt, user_input, is_seed, created_at
        FROM images
        ORDER BY id ASC
    """)

    results = cursor.fetchall()
    conn.close()

    images = []
    for row in results:
        images.append({
            "id": row[0],
            "image_url": row[1],
            "prompt": row[2],
            "user_input": row[3],
            "is_seed": bool(row[4]),
            "created_at": row[5]
        })

    return images


def get_image_count():
    """Get total number of images"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM images")
    count = cursor.fetchone()[0]

    conn.close()
    return count
