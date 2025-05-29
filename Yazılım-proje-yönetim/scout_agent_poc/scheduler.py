import time
from apscheduler.schedulers.background import BackgroundScheduler

from db import get_active_tasks, save_snapshot, get_last_snapshot
from scraper import fetch_content, compute_hash, compute_diff


def run_task(task: dict):
    """
    Executes a monitoring task: fetches page, compares hash, saves snapshot, and prints diffs if changes detected.
    """
    task_id = task['task_id']
    url = task['url']
    print(f"🔍 Running Task {task_id}: {url}")

    # Attempt to fetch the page
    try:
        raw_html = fetch_content(url)
    except Exception as e:
        # Log fetch errors and skip this run
        print(f"⚠️ Task {task_id} fetch failed: {e}")
        return

    # Compute hash of fetched content
    new_hash = compute_hash(raw_html)

    # Retrieve the last snapshot
    last_snap = get_last_snapshot(task_id)
    if last_snap is None or new_hash != last_snap['content_hash']:
        # Save new snapshot
        save_snapshot(task_id, new_hash, raw_html)
        if last_snap:
            diff = compute_diff(last_snap['raw_html'], raw_html)
            print(f"⚠️ Change detected for Task {task_id} ({url})")
            print(diff)
        else:
            print(f"ℹ️ Initial snapshot recorded for Task {task_id}")
    else:
        print(f"✅ No change detected for Task {task_id}")


def start_scheduler():
    """
    Loads active tasks and schedules them at their configured frequency.
    """
    scheduler = BackgroundScheduler()
    tasks = get_active_tasks()
    for task in tasks:
        scheduler.add_job(
            run_task,
            trigger='interval',
            hours=task['frequency'],
            args=[task],
            id=str(task['task_id'])
        )

    scheduler.start()
    print("⏱ Scheduler started. Press Ctrl+C to exit.")

    try:
        # Keep the scheduler running
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("🛑 Scheduler stopped.")
