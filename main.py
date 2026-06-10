from fetch_jobs import fetch_jobs, verify_job_exists
from notifier import send_notification
from config import load_config
from job_queue import (
    load_pending_jobs, save_pending_jobs, add_pending_job, 
    get_retry_jobs, mark_sent, increment_attempt, remove_pending_job, cleanup_old_jobs
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting AutoNiq job monitor...")
        config = load_config()
        
        # Step 1: Retry pending jobs from previous runs
        logger.info("Checking for pending jobs to retry...")
        pending_jobs = get_retry_jobs()
        
        for job in pending_jobs:
            try:
                # Verify job still exists
                if not verify_job_exists(job["url"]):
                    logger.info(f"Job no longer exists, removing from queue: {job['title']}")
                    remove_pending_job(job["url"])
                    continue
                
                # Try to send email
                logger.info(f"Retrying job notification (attempt {job['attempts'] + 1}): {job['title']}")
                if send_notification(job, config):
                    mark_sent(job["url"])
                    print_job(job)
                else:
                    increment_attempt(job["url"])
                    
            except Exception as e:
                logger.error(f"Error retrying job: {str(e)}")
                increment_attempt(job["url"])
                continue
        
        # Step 2: Fetch new jobs
        logger.info("Fetching new jobs...")
        new_jobs = fetch_jobs()

        print()
        print(f"Found {len(new_jobs)} new jobs")
        print()

        if not new_jobs:
            logger.info("No new jobs found")
        else:
            # Step 3: Process new jobs
            for job in new_jobs:
                try:
                    # Verify job exists before adding to queue
                    if not verify_job_exists(job["url"]):
                        logger.info(f"Job no longer exists, skipping: {job['title']}")
                        continue
                    
                    # Add to pending queue first
                    add_pending_job(job["url"], job)
                    
                    # Try to send email immediately
                    logger.info(f"Sending notification for new job: {job['title']}")
                    if send_notification(job, config):
                        mark_sent(job["url"])
                        print_job(job)
                    else:
                        logger.warning(f"Failed to send email, will retry: {job['title']}")
                        increment_attempt(job["url"])
                        
                except Exception as e:
                    logger.error(f"Error processing job {job.get('title')}: {str(e)}")
                    increment_attempt(job["url"])
                    continue
        
        # Step 4: Cleanup old jobs
        logger.info("Cleaning up old jobs...")
        cleanup_old_jobs(hours=24)
        
        logger.info("AutoNiq job monitor completed successfully")

    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}", exc_info=True)
        raise


def print_job(job):
    """Print job details to console"""
    print("=" * 60)
    print("Title    :", job["title"])
    print("Location :", job["location"])
    print("Page     :", job.get("page", "N/A"))
    print("URL      :", job["url"])
    print()


if __name__ == "__main__":
    main()