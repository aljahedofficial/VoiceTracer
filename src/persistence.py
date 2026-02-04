"""
VoiceTracer Persistence Module

Handles session management, auto-save, and recovery.
"""

import json
import sqlite3
import os
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from pathlib import Path


class SessionDatabase:
    """SQLite database for session management."""
    
    def __init__(self, db_path: str = ".voicetracer/sessions.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data JSON
            )
        """)
        
        # Document pairs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_pairs (
                doc_pair_id TEXT PRIMARY KEY,
                session_id TEXT,
                original_text TEXT,
                edited_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Analysis results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                result_id TEXT PRIMARY KEY,
                doc_pair_id TEXT,
                session_id TEXT,
                metrics_json JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doc_pair_id) REFERENCES document_pairs(doc_pair_id),
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Recovery snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recovery_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                session_id TEXT,
                snapshot_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_session(self, session_id: str, data: Dict) -> bool:
        """Save or update a session."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            data_json = json.dumps(data)
            
            cursor.execute("""
                INSERT OR REPLACE INTO sessions 
                (session_id, data, last_activity)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (session_id, data_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Dict]:
        """Load a session from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data FROM sessions WHERE session_id = ?
            """, (session_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def save_document_pair(self, session_id: str, doc_pair) -> bool:
        """Save a document pair."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO document_pairs 
                (doc_pair_id, session_id, original_text, edited_text)
                VALUES (?, ?, ?, ?)
            """, (doc_pair.id, session_id, doc_pair.original_text, doc_pair.edited_text))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving document pair: {e}")
            return False
    
    def load_document_pair(self, doc_pair_id: str) -> Optional[tuple]:
        """Load a document pair."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT original_text, edited_text FROM document_pairs 
                WHERE doc_pair_id = ?
            """, (doc_pair_id,))
            
            result = cursor.fetchone()
            conn.close()
            return result
        except Exception as e:
            print(f"Error loading document pair: {e}")
            return None
    
    def save_analysis_result(self, session_id: str, doc_pair_id: str, result_id: str, metrics: Dict) -> bool:
        """Save analysis results."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metrics_json = json.dumps(metrics)
            
            cursor.execute("""
                INSERT INTO analysis_results 
                (result_id, doc_pair_id, session_id, metrics_json)
                VALUES (?, ?, ?, ?)
            """, (result_id, doc_pair_id, session_id, metrics_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving analysis result: {e}")
            return False
    
    def save_recovery_snapshot(self, session_id: str, snapshot_id: str, snapshot: Dict) -> bool:
        """Save a recovery snapshot."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            snapshot_json = json.dumps(snapshot)
            
            cursor.execute("""
                INSERT INTO recovery_snapshots 
                (snapshot_id, session_id, snapshot_data)
                VALUES (?, ?, ?)
            """, (snapshot_id, session_id, snapshot_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving recovery snapshot: {e}")
            return False
    
    def load_latest_recovery_snapshot(self, session_id: str) -> Optional[Dict]:
        """Load the latest recovery snapshot for a session."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT snapshot_data FROM recovery_snapshots 
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (session_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
        except Exception as e:
            print(f"Error loading recovery snapshot: {e}")
            return None
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Delete sessions older than specified days."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute("""
                DELETE FROM sessions 
                WHERE last_activity < ?
            """, (cutoff_date,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            return deleted
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")
            return 0


class AutoSaveManager:
    """Manages auto-save functionality."""
    
    def __init__(self, db: SessionDatabase, interval_seconds: int = 30):
        self.db = db
        self.interval = interval_seconds
        self.last_save = {}
    
    def should_save(self, session_id: str) -> bool:
        """Check if auto-save should occur."""
        now = datetime.now()
        last = self.last_save.get(session_id)
        
        if last is None:
            return True
        
        return (now - last).total_seconds() >= self.interval
    
    def create_snapshot(self, session_id: str, streamlit_session_state: Dict) -> Dict:
        """Create a recovery snapshot from current session state."""
        snapshot = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'state': {
                'original_text': streamlit_session_state.get('original_input', ''),
                'edited_text': streamlit_session_state.get('edited_input', ''),
                'current_step': streamlit_session_state.get('nav_step', 1),
            }
        }
        
        if 'doc_pair' in streamlit_session_state:
            snapshot['state']['doc_pair_id'] = streamlit_session_state['doc_pair'].id
        
        if 'analysis_result' in streamlit_session_state:
            snapshot['state']['result_id'] = streamlit_session_state['analysis_result'].doc_pair_id
        
        return snapshot
    
    def auto_save(self, session_id: str, streamlit_session_state: Dict, force: bool = False) -> bool:
        """Perform auto-save if conditions are met."""
        if not force and not self.should_save(session_id):
            return False
        
        snapshot = self.create_snapshot(session_id, streamlit_session_state)
        
        success = self.db.save_recovery_snapshot(
            session_id,
            f"snapshot_{datetime.now().timestamp()}",
            snapshot
        )
        
        if success:
            self.last_save[session_id] = datetime.now()
        
        return success


class SessionRecovery:
    """Handles session recovery on reload."""
    
    def __init__(self, db: SessionDatabase):
        self.db = db
    
    def recover_session(self, session_id: str) -> Optional[Dict]:
        """Recover session state from latest snapshot."""
        snapshot = self.db.load_latest_recovery_snapshot(session_id)
        return snapshot
    
    def apply_recovery(self, snapshot: Dict, streamlit_session_state: Dict) -> None:
        """Apply recovered snapshot to current session state."""
        if not snapshot or 'state' not in snapshot:
            return
        
        state = snapshot['state']
        
        # Restore text inputs
        if 'original_text' in state:
            streamlit_session_state['original_input'] = state['original_text']
        
        if 'edited_text' in state:
            streamlit_session_state['edited_input'] = state['edited_text']
        
        # Restore navigation
        if 'current_step' in state:
            streamlit_session_state['nav_step'] = state['current_step']


# Storage utilities for exporting data
class DataStorage:
    """Utilities for storing and retrieving analysis data."""
    
    @staticmethod
    def export_to_json_file(data: Dict, filename: str) -> bool:
        """Export data to JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def import_from_json_file(filename: str) -> Optional[Dict]:
        """Import data from JSON file."""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error importing from JSON: {e}")
            return None
    
    @staticmethod
    def export_to_csv_file(data: List[Dict], filename: str) -> bool:
        """Export list of dicts to CSV file."""
        try:
            if not data:
                return False
            
            import csv
            keys = data[0].keys()
            
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
