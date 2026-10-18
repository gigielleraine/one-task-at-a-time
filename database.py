from contextlib import closing
import sqlite3

DATABASE_NAME = 'tasks.db'

def get_db_connection():
    """Creates a connection that automatically closes when used in a 'with' block."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return closing(conn)

def init_db():
    """Initialises the database table and adds starter tasks if empty."""
    starter_tasks = [
        ('Reply to one unread email',),
        ('Drink a glass of water',),
        ('Clear three items off the desk',),
        ('Stretch for two minutes',)
    ]
    
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
        ''')
        
        # Safely upgrade existing databases that don't have the 'completed' column yet
        columns = [row['name'] for row in conn.execute('PRAGMA table_info(tasks)')]
        if 'completed' not in columns:
            conn.execute('ALTER TABLE tasks ADD COLUMN completed INTEGER NOT NULL DEFAULT 0')
        
        count = conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
        
        if count == 0:
            conn.executemany(
                'INSERT INTO tasks (title) VALUES (?)',
                starter_tasks
            )
        conn.commit()

def get_active_tasks():
    """Fetches only uncompleted tasks (completed = 0)."""
    with get_db_connection() as conn:
        rows = conn.execute(
            'SELECT id, title FROM tasks WHERE completed = 0'
        ).fetchall()
    return rows

def get_completed_tasks():
    """Fetches all completed tasks (completed = 1) for the progress view."""
    with get_db_connection() as conn:
        rows = conn.execute(
            'SELECT id, title FROM tasks WHERE completed = 1 ORDER BY id DESC'
        ).fetchall()
    return rows

def add_task(title):
    """Safely adds a new task to the database."""
    clean_title = title.strip()
    if clean_title and len(clean_title) <= 200:
        with get_db_connection() as conn:
            conn.execute('INSERT INTO tasks (title) VALUES (?)', (clean_title,))
            conn.commit()

def complete_task(task_id):
    """Marks a task as completed (1) instead of deleting it."""
    with get_db_connection() as conn:
        conn.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
        conn.commit()
