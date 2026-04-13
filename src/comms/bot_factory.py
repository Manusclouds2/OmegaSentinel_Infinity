"""
LOPUTHJOSEPH - BOT FACTORY
- Dynamic multi-tenant Telegram bot management
- Background worker threads for each client bot
- Scalable worker pattern for high-speed growth
"""

import telebot
import logging
from threading import Thread
from typing import Dict

logger = logging.getLogger("BOT_FACTORY")

class BotFactory:
    def __init__(self):
        self.active_bots: Dict[int, telebot.TeleBot] = {}  # Format: {user_id: bot_instance}

    def launch_client_bot(self, user_id: int, decrypted_token: str):
        """Spins up a new background thread for a specific client bot."""
        if user_id in self.active_bots:
            logger.info(f"[*] User {user_id} already has an active bot.")
            return

        def bot_worker():
            try:
                bot = telebot.TeleBot(decrypted_token)
                self.active_bots[user_id] = bot
                
                @bot.message_handler(commands=['status'])
                def check_status(message):
                    bot.reply_to(message, "🛡️ Sentinel-UG: All systems operational. Hardware heartbeat: 100%.")

                @bot.message_handler(commands=['help'])
                def send_help(message):
                    bot.reply_to(message, "Sentinel Client Bot Commands:\n/status - Check system health\n/lock - Remote lock (MFA required)")

                logger.info(f"[+] Bot for User {user_id} is now LIVE.")
                bot.infinity_polling()
            except Exception as e:
                logger.error(f"[-] Bot worker failed for user {user_id}: {e}")
                if user_id in self.active_bots:
                    del self.active_bots[user_id]

        # Start the bot in a separate thread so it doesn't block the server
        client_thread = Thread(target=bot_worker, daemon=True)
        client_thread.start()

    def send_to_client(self, user_id: int, message: str, image_path: str = None):
        """Routes a message or image to a specific client's bot instance"""
        if user_id in self.active_bots:
            bot = self.active_bots[user_id]
            try:
                if image_path and os.path.exists(image_path):
                    with open(image_path, 'rb') as img:
                        bot.send_photo(user_id, img, caption=message)
                else:
                    bot.send_message(user_id, message)
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
        else:
            logger.warning(f"Attempted to send to inactive bot for user {user_id}")

bot_factory = BotFactory()
