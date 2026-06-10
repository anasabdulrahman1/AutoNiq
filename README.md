# AutoNiq - Nielsen IQ Job Alerts

A lightweight job monitoring script that scrapes Nielsen IQ careers page for matching job openings in India and sends email notifications.

## Features

✅ **Smart Job Tracking**
- Finds matching jobs across all pages
- Tracks jobs in a queue system to prevent duplicates
- Verifies jobs still exist before sending notifications

✅ **Reliable Email Delivery**
- Retries failed email notifications automatically (up to 3 attempts)
- Only marks jobs as "sent" after successful email delivery
- Cleans up old jobs after 24 hours

✅ **Pagination Support**
- Automatically loops through all available pages
- Stops after 2 consecutive empty pages
- No arbitrary page limits

✅ **Error Handling**
- Comprehensive logging with timestamps
- Graceful error recovery (doesn't crash on failures)
- Connection timeout handling

✅ **Scheduled Execution**
- GitHub Actions workflow runs hourly
- Can be customized to any interval

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Email (Gmail)

#### Enable 2-Factor Authentication:
1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**

#### Generate App Password:
1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Select **Mail** and **Windows Computer**
3. Copy the 16-character password

#### Update `.env` file:
```env
NOTIFICATION_TYPE=email
EMAIL_SENDER=your-email@gmail.com
EMAIL_RECIPIENT=where-to-send@gmail.com
SMTP_PASSWORD=your-16-char-password
```

### 3. Run Manually
```bash
python main.py
```

## How It Works

### Job Queue System

The script uses a smart queue system to ensure no jobs are lost:

```
1. FETCH NEW JOBS
   └─ Check all pages for matching jobs
   
2. VERIFY JOBS EXIST
   └─ Confirm job URLs are still available
   
3. ADD TO QUEUE
   └─ Store in jobs_pending.json with:
      - Title, location, URL
      - Status (pending/sent/failed)
      - Attempt count (max 3 retries)
      - Timestamps
   
4. SEND EMAIL
   ├─ If success → Mark as "sent" ✅
   ├─ If fails → Retry next run (up to 3 times)
   └─ If job removed → Skip (don't track)

5. RETRY PENDING JOBS
   └─ On next run, attempt to send any pending emails
   
6. CLEANUP
   └─ Remove jobs older than 24 hours
```

### Files

- `main.py` - Main entry point
- `fetch_jobs.py` - Web scraping & pagination
- `notifier.py` - Email notification handler
- `config.py` - Configuration management
- `job_queue.py` - Job queue & retry logic
- `.env` - Environment variables (create from template)
- `jobs_pending.json` - Active job queue (auto-generated)

### Filters

**Keywords:** data operations, data process, data processing, operations analyst, process associate

**Locations:** India, Bangalore, Chennai, Hyderabad, Mumbai, Pune, Gurgaon, Noida, Kochi, Kolkata

## GitHub Actions

The workflow runs hourly at the top of each hour. Set up secrets in GitHub:

```
API_KEY
NOTIFICATION_TYPE
EMAIL_SENDER
EMAIL_RECIPIENT
SMTP_PASSWORD
```

## Troubleshooting

### No emails received?
1. Check spam/promotions folder
2. Verify app password has no extra spaces
3. Check script logs for email errors
4. Ensure 2FA is enabled on Gmail

### Job not being found?
1. Verify keywords and locations in `fetch_jobs.py`
2. Check pagination is working (should see pages 1-20+)
3. Run manually to see detailed logs

### Jobs keep retrying?
- Jobs retry up to 3 times if email fails
- After 3 attempts, marked as "failed"
- Old jobs auto-cleanup after 24 hours

## Customization

### Change Email Frequency
Edit `.env`:
```env
UPDATE_INTERVAL=1800  # 30 minutes
```

### Change Keywords
Edit `fetch_jobs.py`:
```python
KEYWORDS = [
    "your",
    "keywords",
    "here"
]
```

### Change Locations
Edit `fetch_jobs.py`:
```python
INDIA_LOCATIONS = [
    "city",
    "names"
]
```

## License

MIT
