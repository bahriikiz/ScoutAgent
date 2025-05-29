import sqlite3
from typing import List, Dict

DB_PATH = "scout_agent.db"

def get_connection() -> sqlite3.Connection:
    """
    Returns a SQLite connection with row access as dict.
    """
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes the database by creating tasks and snapshots tables.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        task_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        recruiter_id TEXT,
        url         TEXT NOT NULL,
        frequency   REAL NOT NULL,
        task_prompt TEXT,
        status      TEXT CHECK(status IN ('active','inactive')) NOT NULL DEFAULT 'active',
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS snapshots (
        snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id     INTEGER NOT NULL,
        content_hash TEXT,
        raw_html    TEXT,
        timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(task_id) REFERENCES tasks(task_id)
    );
    """)
    conn.commit()
    conn.close()


def add_task(recruiter_id: str, url: str, frequency: float, task_prompt: str, status: str = "active") -> int:
    """
    Inserts a new monitoring task and returns its generated task_id.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tasks (recruiter_id, url, frequency, task_prompt, status)
        VALUES (?, ?, ?, ?, ?)
        """, (recruiter_id, url, frequency, task_prompt, status)
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id


def get_active_tasks() -> List[Dict]:
    """
    Retrieves all tasks where status is 'active'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE status='active'")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_snapshot(task_id: int, content_hash: str, raw_html: str):
    """
    Saves a new snapshot record for the given task.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO snapshots (task_id, content_hash, raw_html)
        VALUES (?, ?, ?)
        """, (task_id, content_hash, raw_html)
    )
    conn.commit()
    conn.close()


def get_last_snapshot(task_id: int) -> Dict:
    """
    Returns the most recent snapshot for a task, or None if none exists.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM snapshots WHERE task_id=? ORDER BY timestamp DESC LIMIT 1", (task_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def count_tasks():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM tasks")
    total = c.fetchone()[0]
    conn.close()
    return total

def count_snapshots():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM snapshots")
    total = c.fetchone()[0]
    conn.close()
    return total

def count_changes():
    """
    Kaç farklı snapshot alınmış: (aynı hash olanları saymaz)
    Her görev için değişiklik sayısı = snapshot sayısı - 1 (ilk kayıt hariç).
    Toplam değişiklik = Tüm görevlerin (snapshot - 1) toplamı
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT task_id, COUNT(*) as cnt 
        FROM snapshots GROUP BY task_id
    """)
    total = 0
    for row in c.fetchall():
        total += max(0, row[1] - 1)
    conn.close()
    return total

def last_change_time():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT MAX(timestamp) FROM snapshots")
    ts = c.fetchone()[0]
    conn.close()
    return ts  # None ise henüz hiç snapshot yok!
def delete_task(task_id: int):
    conn = get_connection()
    c = conn.cursor()
    # Önce snapshot'ları sil (yoksa FOREIGN KEY hatası olur)
    c.execute("DELETE FROM snapshots WHERE task_id=?", (task_id,))
    c.execute("DELETE FROM tasks WHERE task_id=?", (task_id,))
    conn.commit()
    conn.close()



if __name__ == "__main__":
    init_db()
    print("Database initialized.")
