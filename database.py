import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.db")


# =========================================================
# 初始化数据库
# =========================================================
def init_db():
    """创建所有数据表（如果不存在）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 用户表
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            email TEXT,
            roles TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS template_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            filetype TEXT NOT NULL,
            description TEXT,
            uploader TEXT NOT NULL,
            upload_at TEXT NOT NULL,
            cover_path TEXT,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    """)

    # 摄影师上传的图片表
    c.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            category TEXT NOT NULL,
            uploader TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            upload_at TEXT NOT NULL,
            reviewed_at TEXT,
            review_note TEXT
        )
    """)

    # 设计师上传的模版文件表
    c.execute("""
        CREATE TABLE IF NOT EXISTS template_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            filetype TEXT NOT NULL,
            description TEXT,
            uploader TEXT NOT NULL,
            upload_at TEXT NOT NULL
        )
    """)

    # 海报历史记录表
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            template_name TEXT NOT NULL,
            bg_path TEXT,
            user_inputs TEXT,
            poster_path TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    conn.commit()   
    # 创建默认管理员账号（如果不存在）
    existing = c.execute(
        "SELECT id FROM users WHERE username = 'admin'"
    ).fetchone()
    if not existing:
        c.execute(
            "INSERT INTO users (username, password_hash, roles, created_at) VALUES (?, ?, ?, ?)",
            ("admin", _hash_password("admin888"), "admin,user", datetime.now().isoformat())
        )

    conn.commit()
    conn.close()


# =========================================================
# 工具函数
# =========================================================
def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# 用户相关
# =========================================================
def register_user(username: str, password: str, email: str = "", roles: list = None) -> tuple[bool, str]:
    """注册新用户，roles 为身份列表如 ['user', 'designer']"""
    if roles is None:
        roles = ["user"]
    roles_str = ",".join(roles)
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, email, roles, created_at) VALUES (?, ?, ?, ?, ?)",
            (username, _hash_password(password), email, roles_str, datetime.now().isoformat())
        )
        conn.commit()
        return True, "注册成功"
    except sqlite3.IntegrityError:
        return False, "用户名已存在，请换一个"
    finally:
        conn.close()


def verify_user(username: str, password: str) -> dict | None:
    """验证用户名和密码，返回用户信息字典或 None"""
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, _hash_password(password))
    ).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_user(username: str) -> dict | None:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def user_has_role(username: str, role: str) -> bool:
    """检查用户是否拥有某个身份"""
    user = get_user(username)
    if not user:
        return False
    return role in user["roles"].split(",")


def _normalize_roles(roles: list[str] | set[str] | tuple[str, ...]) -> list[str]:
    allowed = {"user", "designer", "photographer", "admin"}
    ordered = ["user", "designer", "photographer", "admin"]
    cleaned = {role for role in roles if role in allowed}
    if not cleaned:
        cleaned.add("user")
    return [role for role in ordered if role in cleaned]


def add_role_to_user(username: str, role: str) -> bool:
    """给用户增加一个身份。admin 只能由管理后台调用。"""
    if role not in {"user", "designer", "photographer", "admin"}:
        return False
    user = get_user(username)
    if not user:
        return False
    roles = _normalize_roles(set(user["roles"].split(",")) | {role})
    conn = _get_conn()
    conn.execute("UPDATE users SET roles = ? WHERE username = ?", (",".join(roles), username))
    conn.commit()
    conn.close()
    return True


def update_user_roles(username: str, roles: list[str]) -> bool:
    """管理员更新用户身份。"""
    if not get_user(username):
        return False
    normalized = _normalize_roles(roles)
    conn = _get_conn()
    conn.execute("UPDATE users SET roles = ? WHERE username = ?", (",".join(normalized), username))
    conn.commit()
    conn.close()
    return True


def get_all_users() -> list[dict]:
    conn = _get_conn()
    rows = conn.execute("SELECT id, username, email, roles, created_at FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =========================================================
# 摄影师图片相关
# =========================================================
PHOTO_CATEGORIES = ["禅意空间", "禅意项目", "自然风光", "其他"]

ZEN_PROJECT_SUBCATEGORIES = [
    "安心禅茶",
    "正念球",
    "健康大循环",
    "按导",
    "正念抄经",
    "正念咖啡",
    "读书会",
    "静心蔬食",
    "静心插花",
]


def save_photo_record(filename: str, filepath: str, category: str, uploader: str) -> int:
    """保存摄影师上传的图片记录，返回记录 id"""
    conn = _get_conn()
    cur = conn.execute(
        "INSERT INTO photos (filename, filepath, category, uploader, status, upload_at) VALUES (?, ?, ?, ?, 'pending', ?)",
        (filename, filepath, category, uploader, datetime.now().isoformat())
    )
    conn.commit()
    photo_id = cur.lastrowid
    conn.close()
    return photo_id


def get_photos(status: str = None, category: str = None) -> list[dict]:
    """获取图片列表，可按状态和分类筛选"""
    conn = _get_conn()
    query = "SELECT * FROM photos WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY upload_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def review_photo(photo_id: int, action: str, note: str = "") -> bool:
    """管理员审核图片，action='approve' 或 'reject'"""
    status = "approved" if action == "approve" else "rejected"
    conn = _get_conn()
    conn.execute(
        "UPDATE photos SET status = ?, reviewed_at = ?, review_note = ? WHERE id = ?",
        (status, datetime.now().isoformat(), note, photo_id)
    )
    conn.commit()
    conn.close()
    return True


def get_approved_photos(category: str = None) -> list[dict]:
    if category and category == "禅意项目":
        conn = _get_conn()
        rows = conn.execute(
            "SELECT * FROM photos WHERE status='approved' AND (category LIKE '禅意项目/%' OR category = '禅意项目') ORDER BY upload_at DESC"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    return get_photos(status="approved", category=category)


# =========================================================
# 设计师模版文件相关
# =========================================================
def save_template_file_record(filename: str, filepath: str, filetype: str,
                               description: str, uploader: str, cover_path: str = None) -> int:
    conn = _get_conn()
    cur = conn.execute(
        "INSERT INTO template_files (filename, filepath, filetype, description, uploader, upload_at, cover_path, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')",
        (filename, filepath, filetype, description, uploader, datetime.now().isoformat(), cover_path)
    )
    conn.commit()
    fid = cur.lastrowid
    conn.close()
    return fid


def get_template_files(status: str = None) -> list[dict]:
    conn = _get_conn()
    query = "SELECT * FROM template_files WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY upload_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def review_template_file(file_id: int, action: str, note: str = "") -> bool:
    status = "approved" if action == "approve" else "rejected"
    conn = _get_conn()
    conn.execute(
        "UPDATE template_files SET status = ? WHERE id = ?",
        (status, file_id)
    )
    conn.commit()
    conn.close()
    return True


# =========================================================
# 历史记录相关
# =========================================================
def save_history(username: str, template_name: str, bg_path: str,
                 user_inputs: str, poster_path: str) -> int:
    conn = _get_conn()
    cur = conn.execute(
        "INSERT INTO history (username, template_name, bg_path, user_inputs, poster_path, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (username, template_name, bg_path, user_inputs, poster_path, datetime.now().isoformat())
    )
    conn.commit()
    hid = cur.lastrowid
    conn.close()
    return hid


def get_user_history(username: str) -> list[dict]:
    """获取某用户的所有历史记录，最新的在前"""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM history WHERE username = ? ORDER BY created_at DESC",
        (username,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_history_record(record_id: int) -> dict | None:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM history WHERE id = ?", (record_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_history_record(record_id: int, username: str) -> bool:
    """删除历史记录（只能删自己的）"""
    conn = _get_conn()
    conn.execute(
        "DELETE FROM history WHERE id = ? AND username = ?",
        (record_id, username)
    )
    conn.commit()
    conn.close()
    return True
