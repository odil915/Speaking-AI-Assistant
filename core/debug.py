import datetime

LOG_FILE = "outputs.log"

def log_debug(category, content):
    """
    Logs debug info to outputs.log with timestamps.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n{'='*20}\n[{timestamp}] [{category}]\n{content}\n{'='*20}\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
