import os
import sys
import subprocess
import time
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.responders.telegram_bot import LoputhJosephTelegramBot

def start_watchdog():
    """
    The Watchdog is a lightweight background service that stays active 
    even when the main LOPUTHJOSEPH suite is off, allowing for remote activation.
    """
    print("[*] LOPUTHJOSEPH WATCHDOG: INITIALIZING...")
    
    # Load configuration
    load_dotenv()
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    ALLOWED_ID = os.environ.get("TELEGRAM_ALLOWED_USER_ID")
    
    if not TOKEN or not ALLOWED_ID or TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("[!] CRITICAL: Telegram credentials missing. Watchdog cannot start.")
        return

    print(f"[*] WATCHDOG ONLINE. LISTENING FOR REMOTE COMMANDS FROM ID: {ALLOWED_ID}")
    
    # Start the bot in the main thread of this script
    # The bot's /activate command will trigger 'python control.py activate'
    bot = LoputhJosephTelegramBot(TOKEN, ALLOWED_ID)
    bot.run()

if __name__ == "__main__":
    try:
        start_watchdog()
    except KeyboardInterrupt:
        print("\n[*] Watchdog shutting down...")
    except Exception as e:
        print(f"[!] Watchdog error: {e}")
        time.sleep(10)
        # Restart attempt
        os.execv(sys.executable, ['python'] + sys.argv)
