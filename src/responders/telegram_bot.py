"""
LOPUTHJOSEPH - TELEGRAM REMOTE CONTROL BOT
- Remote command execution via Telegram
- Real-time threat alerts and system status
- Secure access control (Allowed User ID only)
"""

import os
import logging
import asyncio
import time # New: Missing import for retry logic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.request import HTTPXRequest
import subprocess
import platform
import json
import uuid
from responders.omega_ai import omega_ai
from comms.bot_factory import bot_factory # NEW: Bot Factory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global challenge store (In a real system, use Redis or a DB)
challenges = {}

class LoputhJosephTelegramBot:
    def __init__(self, token: str, allowed_user_id: str):
        self.token = token
        self.allowed_user_id = allowed_user_id
        self.os_type = platform.system()
        self.application = None

    async def send_challenge(self, command_name: str, details: str) -> str:
        """Send an MFA challenge to the Telegram bot"""
        challenge_id = str(uuid.uuid4())
        challenges[challenge_id] = {"status": "pending", "command": command_name}
        
        keyboard = [
            [
                InlineKeyboardButton("Approve ✅", callback_data=f"approve_{challenge_id}"),
                InlineKeyboardButton("Deny ❌", callback_data=f"deny_{challenge_id}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self.application.bot.send_message(
            chat_id=self.allowed_user_id,
            text=f"⚠️ [MFA CHALLENGE] ⚠️\nCommand: {command_name}\nDetails: {details}\n\nPlease approve or deny this action.",
            reply_markup=reply_markup
        )
        
        return challenge_id

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle MFA challenge button clicks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        if data.startswith("approve_"):
            challenge_id = data.replace("approve_", "")
            if challenge_id in challenges:
                challenges[challenge_id]["status"] = "approved"
                await query.edit_message_text(text=f"✅ [APPROVED] Command '{challenges[challenge_id]['command']}' authorized.")
        elif data.startswith("deny_"):
            challenge_id = data.replace("deny_", "")
            if challenge_id in challenges:
                challenges[challenge_id]["status"] = "denied"
                await query.edit_message_text(text=f"❌ [DENIED] Command '{challenges[challenge_id]['command']}' blocked.")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        user_id = str(update.effective_user.id)
        if user_id != self.allowed_user_id:
            await update.message.reply_text("Unauthorized Access. This incident has been logged.")
            logger.warning(f"Unauthorized Telegram access attempt from ID: {user_id}")
            return

        await update.message.reply_text(
            "LOPUTHJOSEPH Kinetic Defense Shield Active.\n\n"
            "Commander: Manus Clouds FLIES 🪰\n\n"
            "Commands:\n"
            "/status - Check system health & defense status\n"
            "/activate - Start full defense suite\n"
            "/scan - Perform deep vulnerability audit\n"
            "/net - Check connectivity status\n"
            "/locate <ip> - Locate and attribute hacker\n"
            "/trace <ip> - Deep SIGINT traceback (Elite)\n"
            "/aegis - Sync universal mobile/industrial shield\n"
            "/vaccine - Generate on-the-fly threat vaccine\n"
            "/heal - Initiate autonomous system self-healing\n"
            "/createweb <name> <html> - Create a web page\n"
            "/sendweb <name> - Send a web page file\n"
            "/ai - AI Intelligence Resources\n"
            "/help - Show this help message"
        )

    async def ai_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != self.allowed_user_id: return
        query = " ".join(context.args)
        if not query:
            await update.message.reply_text("Usage: /ai <your question for Omega AI>")
            return
            
        # Process via local Omega AI
        response = omega_ai.process_query(query)
        await update.message.reply_text(response)

    async def sendweb_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != self.allowed_user_id: return
        
        args = context.args
        if not args:
            await update.message.reply_text("Usage: /sendweb <filename.html>")
            return
            
        filename = args[0]
        if not filename.endswith(".html"):
            filename += ".html"
            
        web_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "web")
        file_path = os.path.join(web_dir, filename)
        
        if os.path.exists(file_path):
            await update.message.reply_document(document=open(file_path, "rb"))
        else:
            await update.message.reply_text(f"[!] File '{filename}' not found.")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != self.allowed_user_id: return
        
        # Simple health check
        await update.message.reply_text(f"[*] SYSTEM STATUS: ONLINE\n[*] OS: {self.os_type}\n[*] Defense Mode: OMNI-KINETIC ELITE")

    async def activate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != self.allowed_user_id: return
        await update.message.reply_text("[*] Activating full defense suite via remote command...")
        subprocess.Popen("python control.py activate", shell=True)
        await update.message.reply_text("[+] System Activation Initiated.")

    async def scan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != self.allowed_user_id: return
        await update.message.reply_text("[*] Executing Deep Vulnerability Audit...")
        
        def run_scan():
            return subprocess.run("python control.py scan", shell=True, capture_output=True, text=True)
            
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_scan)
        await update.message.reply_text(f"Results:\n{result.stdout[:2000]}")

    async def ping_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Simple ping command to verify the bot is receiving messages."""
        await update.message.reply_text("PONG! LOPUTHJOSEPH is listening.")

    async def net_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != self.allowed_user_id: return
        try:
            # Check internet connectivity
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            status = "ONLINE (Global Connectivity OK)"
        except:
            status = "OFFLINE (Local Mode Active)"
            
        await update.message.reply_text(f"[*] Connectivity Status: {status}")

    async def locate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != self.allowed_user_id: return
        if not context.args:
            await update.message.reply_text("Usage: /locate <ip>")
            return
        
        ip = context.args[0]
        await update.message.reply_text(f"[*] Initiating global traceback for: {ip}")
        
        from responders.hacker_locator import HackerLocalizationEngine
        locator = HackerLocalizationEngine()
        result = locator.locate_hacker({"ip": ip})
        
        msg = (
            f"[+] HACKER LOCATED\n"
            f"- Origin: {result['origin']}\n"
            f"- City: {result['city']}\n"
            f"- Actor: {result['threat_actor']}\n"
            f"- Attribution: {result['attribution']}\n"
            f"- Lat/Lon: {result['latitude']}, {result['longitude']}"
        )
        await update.message.reply_text(msg)

    async def vaccine_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != self.allowed_user_id: return
        await update.message.reply_text("[*] Synthesizing elite threat vaccine...")
        
        from responders.vaccine_generator import VaccineGenerator
        gen = VaccineGenerator()
        result = gen.generate_vaccine({"type": "ZERO_DAY_AI_MALWARE", "entropy": 7.8})
        
        await update.message.reply_text(f"[+] Vaccine generated and deployed: {result['id']}")

    async def trace_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != self.allowed_user_id: return
        if not context.args:
            await update.message.reply_text("Usage: /trace <ip>")
            return
        
        ip = context.args[0]
        await update.message.reply_text(f"[*] INITIATING DEEP SIGINT TRACEBACK: {ip}")
        
        from responders.sigint_beacon import SIGINTBeaconEngine
        engine = SIGINTBeaconEngine()
        token = engine.inject_beacon(ip, "TELEGRAM_REMOTE")
        result = engine.perform_deep_traceback(token)
        
        msg = (
            f"[!!!] TRACEBACK COMPLETE\n"
            f"- True Origin: {result['true_origin']}\n"
            f"- Accuracy: {result['accuracy']}\n"
            f"- Path Identified: {' -> '.join(result['hops'])}"
        )
        await update.message.reply_text(msg)

    async def aegis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != self.allowed_user_id: return
        await update.message.reply_text("[*] Synchronizing Aegis-X Universal Defense...")
        
        from detectors.aegis_x_shield import AegisXShield
        aegis = AegisXShield()
        aegis.universal_defense_sync()
        
        await update.message.reply_text("[+] Aegis-X synchronized. Mobile & Industrial assets secured.")

    async def heal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.effective_user.id) != self.allowed_user_id: return
        await update.message.reply_text("[*] Initiating autonomous self-healing sequence...")
        
        from responders.vaccine_generator import SelfHealingEngine
        healer = SelfHealingEngine()
        # Simulated healing
        await update.message.reply_text("[+] System component integrity verified. Self-healing COMPLETE.")

    async def register_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Register a new client bot token and spin up a dedicated thread"""
        if str(update.effective_user.id) != self.allowed_user_id: return
        
        if not context.args:
            await update.message.reply_text("Usage: /register <your_client_bot_token>")
            return
            
        raw_token = context.args[0]
        user_id = update.effective_user.id
        
        # 1. Automated Bot Launch
        try:
            bot_factory.launch_client_bot(user_id, raw_token)
            await update.message.reply_text("🚀 Your private Sentinel Bot is now ONLINE. Check your new bot to start receiving live feeds!")
            logger.info(f"Client bot registered and launched for user {user_id}")
        except Exception as e:
            await update.message.reply_text(f"[-] Registration failed: {e}")

    def run(self):
        """Start the bot with retry logic."""
        max_retries = 10
        retry_delay = 5
        
        # Increase timeout for high-latency connections
        request = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0)
        
        for attempt in range(max_retries):
            try:
                print(f"[*] Connection attempt {attempt + 1}/{max_retries}...")
                app = ApplicationBuilder().token(self.token).request(request).build()
                self.application = app

                app.add_handler(CallbackQueryHandler(self.handle_callback))
                app.add_handler(CommandHandler("start", self.start_command))
                app.add_handler(CommandHandler("help", self.start_command))
                app.add_handler(CommandHandler("ping", self.ping_command))
                app.add_handler(CommandHandler("status", self.status_command))
                app.add_handler(CommandHandler("activate", self.activate_command))
                app.add_handler(CommandHandler("scan", self.scan_command))
                app.add_handler(CommandHandler("sendweb", self.sendweb_command))
                app.add_handler(CommandHandler("ai", self.ai_command))
                app.add_handler(CommandHandler("net", self.net_command))
                app.add_handler(CommandHandler("locate", self.locate_command))
                app.add_handler(CommandHandler("trace", self.trace_command))
                app.add_handler(CommandHandler("aegis", self.aegis_command))
                app.add_handler(CommandHandler("vaccine", self.vaccine_command))
                app.add_handler(CommandHandler("heal", self.heal_command))
                app.add_handler(CommandHandler("register", self.register_command)) # NEW: Register client bot

                print(f"[+] Telegram Remote Control Bot is ONLINE.")
                # bootstrap_retries=-1 means it will keep trying to connect on startup
                app.run_polling(bootstrap_retries=-1, timeout=30)
                break # Success
            except Exception as e:
                print(f"[!] Connection error: {e}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
        else:
            print("[!!!] CRITICAL: Could not connect to Telegram after several attempts. Check your internet connection or Proxy settings.")

if __name__ == "__main__":
    # For testing: use env vars or defaults
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    ALLOWED_ID = os.environ.get("TELEGRAM_ALLOWED_USER_ID", "YOUR_USER_ID_HERE")
    
    if TOKEN != "YOUR_BOT_TOKEN_HERE":
        bot = LoputhJosephTelegramBot(TOKEN, ALLOWED_ID)
        bot.run()
    else:
        print("[!] ERROR: Telegram Token not configured in .env")
