"""
Database models and operations for lead scoring API
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

class Database:
    def __init__(self, db_path: str = "lead_scores.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table for scored domains
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scored_domains (
                domain TEXT PRIMARY KEY,
                score INTEGER NOT NULL,
                grade TEXT NOT NULL,
                priority TEXT NOT NULL,
                attributes TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table for batch jobs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_jobs (
                job_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                total_domains INTEGER NOT NULL,
                processed_domains INTEGER DEFAULT 0,
                successful_domains INTEGER DEFAULT 0,
                failed_domains INTEGER DEFAULT 0,
                webhook_url TEXT,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        # Index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_domain_updated
            ON scored_domains(last_updated DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_job_status
            ON batch_jobs(status, created_at DESC)
        """)

        conn.commit()
        conn.close()

    def get_scored_domain(self, domain: str) -> Optional[Dict]:
        """Get a previously scored domain from cache"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT domain, score, grade, priority, attributes, last_updated
            FROM scored_domains
            WHERE domain = ?
        """, (domain.lower(),))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "domain": row["domain"],
                "score": row["score"],
                "grade": row["grade"],
                "priority": row["priority"],
                "attributes": json.loads(row["attributes"]) if row["attributes"] else {},
                "last_updated": row["last_updated"]
            }
        return None

    def save_scored_domain(self, domain: str, score: int, grade: str,
                           priority: str, attributes: Dict = None):
        """Save a scored domain to cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO scored_domains
            (domain, score, grade, priority, attributes, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            domain.lower(),
            score,
            grade,
            priority,
            json.dumps(attributes) if attributes else None,
            datetime.now()
        ))

        conn.commit()
        conn.close()

    def create_batch_job(self, job_id: str, total_domains: int,
                        webhook_url: Optional[str] = None) -> None:
        """Create a new batch job"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO batch_jobs
            (job_id, status, total_domains, webhook_url, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (job_id, "processing", total_domains, webhook_url, datetime.now()))

        conn.commit()
        conn.close()

    def update_batch_job(self, job_id: str, processed: int = None,
                        successful: int = None, failed: int = None,
                        status: str = None, results: Dict = None):
        """Update batch job progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []

        if processed is not None:
            updates.append("processed_domains = ?")
            params.append(processed)

        if successful is not None:
            updates.append("successful_domains = ?")
            params.append(successful)

        if failed is not None:
            updates.append("failed_domains = ?")
            params.append(failed)

        if status:
            updates.append("status = ?")
            params.append(status)

        if results:
            updates.append("results = ?")
            params.append(json.dumps(results))

        if status == "completed" or status == "failed":
            updates.append("completed_at = ?")
            params.append(datetime.now())

        params.append(job_id)

        cursor.execute(f"""
            UPDATE batch_jobs
            SET {', '.join(updates)}
            WHERE job_id = ?
        """, params)

        conn.commit()
        conn.close()

    def get_batch_job(self, job_id: str) -> Optional[Dict]:
        """Get batch job status"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM batch_jobs
            WHERE job_id = ?
        """, (job_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "job_id": row["job_id"],
                "status": row["status"],
                "total_domains": row["total_domains"],
                "processed_domains": row["processed_domains"],
                "successful_domains": row["successful_domains"],
                "failed_domains": row["failed_domains"],
                "webhook_url": row["webhook_url"],
                "results": json.loads(row["results"]) if row["results"] else None,
                "created_at": row["created_at"],
                "completed_at": row["completed_at"]
            }
        return None

    def get_batch_domains(self, domains: List[str]) -> Dict[str, Dict]:
        """Get multiple domains from cache"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Convert to lowercase for lookup
        domains_lower = [d.lower() for d in domains]
        placeholders = ','.join('?' * len(domains_lower))

        cursor.execute(f"""
            SELECT domain, score, grade, priority, attributes, last_updated
            FROM scored_domains
            WHERE domain IN ({placeholders})
        """, domains_lower)

        results = {}
        for row in cursor.fetchall():
            results[row["domain"]] = {
                "domain": row["domain"],
                "score": row["score"],
                "grade": row["grade"],
                "priority": row["priority"],
                "attributes": json.loads(row["attributes"]) if row["attributes"] else {},
                "last_updated": row["last_updated"]
            }

        conn.close()
        return results