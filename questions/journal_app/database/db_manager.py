import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from .encryption import EncryptionManager


class DatabaseManager:
    def __init__(self, db_path: str, encryption_manager: EncryptionManager):
        self.db_path = db_path
        self.encryption = encryption_manager
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATETIME NOT NULL,
                prompt TEXT NOT NULL,
                content BLOB NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_config (
                key TEXT PRIMARY KEY,
                value BLOB NOT NULL
            )
        ''')
        
        self.conn.commit()
    
    def save_entry(self, prompt: str, content: str) -> int:
        now = datetime.now()
        encrypted_content = self.encryption.encrypt(content)
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO entries (date, prompt, content, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (now, prompt, encrypted_content, now, now))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_entry(self, entry_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_dict(row)
        return None
    
    def search_by_date(self, date: datetime) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM entries 
            WHERE DATE(date) = DATE(?)
            ORDER BY date DESC
        ''', (date,))
        
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def search_by_text(self, search_term: str) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM entries ORDER BY date DESC')
        
        results = []
        search_term_lower = search_term.lower()
        
        for row in cursor.fetchall():
            entry = self._row_to_dict(row)
            if (search_term_lower in entry['prompt'].lower() or 
                search_term_lower in entry['content'].lower()):
                results.append(entry)
        
        return results
    
    def get_all_entries(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM entries ORDER BY date DESC')
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def update_entry(self, entry_id: int, content: str) -> bool:
        encrypted_content = self.encryption.encrypt(content)
        now = datetime.now()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE entries 
            SET content = ?, updated_at = ?
            WHERE id = ?
        ''', (encrypted_content, now, entry_id))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_entry(self, entry_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def save_config(self, key: str, value: str):
        encrypted_value = self.encryption.encrypt(value)
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO app_config (key, value)
            VALUES (?, ?)
        ''', (key, encrypted_value))
        self.conn.commit()
    
    def get_config(self, key: str) -> Optional[str]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM app_config WHERE key = ?', (key,))
        row = cursor.fetchone()
        
        if row:
            return self.encryption.decrypt(row[0])
        return None
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        return {
            'id': row['id'],
            'date': datetime.fromisoformat(row['date']) if isinstance(row['date'], str) else row['date'],
            'prompt': row['prompt'],
            'content': self.encryption.decrypt(row['content']),
            'created_at': datetime.fromisoformat(row['created_at']) if isinstance(row['created_at'], str) else row['created_at'],
            'updated_at': datetime.fromisoformat(row['updated_at']) if isinstance(row['updated_at'], str) else row['updated_at']
        }
    
    def close(self):
        if self.conn:
            self.conn.close()
