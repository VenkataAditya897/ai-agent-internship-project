import sqlite3
import json
import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "memory.db"

class MemoryManager:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT,
                format TEXT,
                intent TEXT,
                content TEXT,
                conversation_id TEXT,
                timestamp TEXT
            )
        ''')
        self.conn.commit()

    def log_input(self, source_type, format, intent, content, conversation_id=None, timestamp=None):
        cursor = self.conn.cursor()
        # timestamp = datetime.datetime.utcnow().isoformat()
        timestamp = timestamp or datetime.datetime.utcnow().isoformat()
        cursor.execute('''
            INSERT INTO memory (source_type, format, intent, content, conversation_id, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (source_type, format, intent, json.dumps(content), conversation_id, timestamp))
        self.conn.commit()

    def get_by_conversation_id(self, conversation_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM memory WHERE conversation_id = ?
        ''', (conversation_id,))
        rows = cursor.fetchall()
        return rows

    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM memory')
        return cursor.fetchall()

    def delete_log(self, log_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM memory WHERE id = ?', (log_id,))
        self.conn.commit()
    def get_filtered_logs(self, format_filter=None, intent_filter=None, conversation_id_filter=None):
        cursor = self.conn.cursor()
        query = 'SELECT * FROM memory WHERE 1=1'
        params = []

        if format_filter:
            query += ' AND format = ?'
            params.append(format_filter)

        if intent_filter:
            query += ' AND intent LIKE ?'
            params.append(f"%{intent_filter}%")

        if conversation_id_filter:
            query += ' AND conversation_id LIKE ?'
            params.append(f"%{conversation_id_filter}%")

        cursor.execute(query, params)
        return cursor.fetchall()
