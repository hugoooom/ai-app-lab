"""SQLite 存储层：把对话存下来。

为什么需要它：模型本身没有记忆。每次请求，你都得把历史一起传过去。
历史存在哪里、怎么取，就是这个文件负责的事。

表结构：

    messages(id, session_id, role, content, created_at)

    session_id  一次对话的标识，同一个人可以开多个会话
    role        system / user / assistant
    created_at  写入时间，SQLite 自动填
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "chat.db"


def get_conn() -> sqlite3.Connection:
    """每次操作都新开一个连接。SQLite 的连接不要跨线程复用。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 让查询结果能按列名取值：row["content"]
    return conn


def init_db() -> None:
    """建表。IF NOT EXISTS 保证重复执行不报错。"""
    conn = get_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, id)"
        )
        conn.commit()
    finally:
        conn.close()


def save_message(session_id: str, role: str, content: str) -> None:
    """追加一条消息。

    注意 SQL 里的 ? 占位符：不要用 f-string 拼 SQL。
    拼字符串就是 SQL 注入的入口，参数化查询是默认写法。
    """
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content),
        )
        conn.commit()
    finally:
        conn.close()


def load_messages(session_id: str, limit: int = 10) -> list[dict]:
    """取最近 limit 条，按时间正序返回。

    为什么要 limit：上下文越长，token 越多、越贵、越慢，而且模型有窗口上限。
    真实项目里这个 limit 是核心参数之一。
    """
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT role, content FROM messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
    finally:
        conn.close()

    # 查出来是倒序（最近的在前），翻转成正序再交给模型
    return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]


if __name__ == "__main__":
    # 单独测试这一层：python db.py
    init_db()
    save_message("selftest", "user", "你好")
    save_message("selftest", "assistant", "你好，有什么可以帮你？")
    print(load_messages("selftest"))
