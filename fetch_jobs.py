import requests
import json
import os
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://careers.smartrecruiters.com/NielsenIQ/api/groups?page="
SEEN_JOBS_FILE = "jobs_seen.json"

KEYWORDS = [
"data operations",
"data process",
"data processing",
"operations analyst",
"process associate",
]

INDIA_LOCATIONS = [
"india",
"bangalore",
"bengaluru",
"chennai",
"hyderabad",
"mumbai",
"pune",
"gurgaon",
"gurugram",
"noida",
"kochi",
"kolkata",
]

def load_seen_jobs():
    """Load previously seen job URLs"""
    try:
        if os.path.exists(SEEN_JOBS_FILE):
            with open(SEEN_JOBS_FILE, 'r') as f:
                seen = set(json.load(f))
                logger.info(f"Loaded {len(seen)} previously seen jobs")
                return seen
    except Exception as e:
        logger.warning(f"Could not load seen jobs file: {str(e)}")
    return set()


def save_seen_jobs(seen):
    """Save seen job URLs"""
    try:
        with open(SEEN_JOBS_FILE, 'w') as f:
            json.dump(list(seen), f)
        logger.info(f"Saved {len(seen)} seen jobs")
    except Exception as e:
        logger.error(f"Failed to save seen jobs: {str(e)}")


def verify_job_exists(job_url: str) -> bool:
    """Verify if a job URL still exists on the page"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(job_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            logger.debug(f"Job verified: {job_url}")
            return True
        else:
            logger.warning(f"Job not found (status {response.status_code}): {job_url}")
            return False
            
    except Exception as e:
        logger.debug(f"Error verifying job: {str(e)}")
        return False


def fetch_jobs():
    """Fetch jobs from all available pages with pagination"""
    from job_queue import load_pending_jobs
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    pending = load_pending_jobs()
    all_jobs = []
    page = 1
    empty_pages = 0

    while empty_pages < 2:  # Stop after 2 consecutive empty pages
        try:
            url = f"{BASE_URL}{page}"
            logger.info(f"Fetching page {page}...")
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            sections = soup.find_all("section")
            
            if not sections:
                empty_pages += 1
                logger.info(f"Page {page} is empty. Empty page count: {empty_pages}")
                page += 1
                continue
            
            empty_pages = 0
            page_jobs = []

            for section in sections:
                try:
                    location_tag = section.find("h3")
                    if location_tag is None:
                        continue

                    location = location_tag.get_text(strip=True)
                    if not any(city in location.lower() for city in INDIA_LOCATIONS):
                        continue

                    for link in section.find_all("a", href=True):
                        try:
                            title_tag = link.find("h4")
                            if title_tag is None:
                                continue

                            title = title_tag.get_text(strip=True)
                            url = link["href"]

                            if any(keyword in title.lower() for keyword in KEYWORDS):
                                # Skip if already in queue (pending or sent)
                                if url not in pending:
                                    job = {
                                        "title": title,
                                        "location": location,
                                        "url": url,
                                        "page": page
                                    }
                                    all_jobs.append(job)
                                    page_jobs.append(job)
                                    logger.debug(f"Found new job: {title}")
                        except Exception as e:
                            logger.debug(f"Error parsing job link: {str(e)}")
                            continue

                except Exception as e:
                    logger.debug(f"Error parsing section: {str(e)}")
                    continue

            logger.info(f"Found {len(page_jobs)} new jobs on page {page}")
            page += 1

        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching page {page}")
            break
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error fetching page {page}")
            break
        except Exception as e:
            logger.error(f"Error fetching page {page}: {str(e)}")
            break

    logger.info(f"Total new jobs found: {len(all_jobs)}")
    return all_jobs
