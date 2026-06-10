"""
Job queue management - handles pending jobs with retry logic
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

JOBS_QUEUE_FILE = "jobs_queue.json"
MAX_RETRY_ATTEMPTS = 3


def load_pending_jobs() -> Dict:
    """Load pending jobs from file"""
    try:
        if os.path.exists(JOBS_QUEUE_FILE):
            with open(JOBS_QUEUE_FILE, 'r') as f:
                jobs = json.load(f)
                logger.info(f"Loaded {len(jobs)} pending jobs")
                return jobs
    except Exception as e:
        logger.warning(f"Could not load pending jobs: {str(e)}")
    return {}


def save_pending_jobs(jobs: Dict) -> None:
    """Save pending jobs to file"""
    try:
        with open(JOBS_QUEUE_FILE, 'w') as f:
            json.dump(jobs, f, indent=2)
        logger.info(f"Saved {len(jobs)} pending jobs")
    except Exception as e:
        logger.error(f"Failed to save pending jobs: {str(e)}")


def add_pending_job(url: str, job_data: Dict) -> None:
    """Add a new job to pending queue"""
    pending = load_pending_jobs()
    pending[url] = {
        "title": job_data.get("title"),
        "location": job_data.get("location"),
        "page": job_data.get("page"),
        "status": "pending",
        "attempts": 0,
        "found_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_attempt": None
    }
    save_pending_jobs(pending)
    logger.info(f"Added job to pending queue: {job_data.get('title')}")


def get_retry_jobs() -> List[Dict]:
    """Get jobs that need retry (status=pending, attempts < MAX)"""
    pending = load_pending_jobs()
    retry_jobs = []
    
    for url, job in pending.items():
        if job.get("status") == "pending" and job.get("attempts", 0) < MAX_RETRY_ATTEMPTS:
            retry_jobs.append({
                "url": url,
                "title": job.get("title"),
                "location": job.get("location"),
                "page": job.get("page"),
                "attempts": job.get("attempts", 0)
            })
    
    if retry_jobs:
        logger.info(f"Found {len(retry_jobs)} jobs to retry")
    
    return retry_jobs


def mark_sent(url: str) -> None:
    """Mark a job as successfully sent"""
    pending = load_pending_jobs()
    if url in pending:
        pending[url]["status"] = "sent"
        pending[url]["sent_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_pending_jobs(pending)
        logger.info(f"Marked job as sent: {pending[url].get('title')}")


def mark_failed(url: str) -> None:
    """Mark a job as failed (max retries reached)"""
    pending = load_pending_jobs()
    if url in pending:
        pending[url]["status"] = "failed"
        save_pending_jobs(pending)
        logger.warning(f"Marked job as failed (max retries): {pending[url].get('title')}")


def increment_attempt(url: str) -> None:
    """Increment retry attempt count"""
    pending = load_pending_jobs()
    if url in pending:
        pending[url]["attempts"] = pending[url].get("attempts", 0) + 1
        pending[url]["last_attempt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if pending[url]["attempts"] >= MAX_RETRY_ATTEMPTS:
            mark_failed(url)
        else:
            save_pending_jobs(pending)
        
        logger.info(f"Job attempt {pending[url]['attempts']}/{MAX_RETRY_ATTEMPTS}: {pending[url].get('title')}")


def remove_pending_job(url: str) -> None:
    """Remove job from pending queue (when job no longer exists on page)"""
    pending = load_pending_jobs()
    if url in pending:
        title = pending[url].get("title")
        del pending[url]
        save_pending_jobs(pending)
        logger.info(f"Removed from queue (job not found on page): {title}")


def cleanup_old_jobs(hours: int = 24) -> None:
    """Remove jobs that have been in queue for too long"""
    pending = load_pending_jobs()
    now = datetime.now()
    updated = False
    
    for url in list(pending.keys()):
        found_at = pending[url].get("found_at")
        if found_at:
            try:
                found_time = datetime.strptime(found_at, "%Y-%m-%d %H:%M:%S")
                age_hours = (now - found_time).total_seconds() / 3600
                
                if age_hours > hours and pending[url].get("status") != "sent":
                    logger.warning(f"Removing job older than {hours}h: {pending[url].get('title')}")
                    del pending[url]
                    updated = True
            except Exception as e:
                logger.debug(f"Could not parse date: {str(e)}")
    
    if updated:
        save_pending_jobs(pending)
