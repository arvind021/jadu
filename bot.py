import logging
import requests
import random
import string
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === CONFIGURATION ===
TELEGRAM_BOT_TOKEN = '7110229849:AAHKRsAERovGQUaOe7mrV008QtYglLmEH30'
SMTP_DEV_API_KEY = 'smtplabs_KHyTXCtUQAnw2zX9yH3d5G5aDqtiaBJaQMPe2ubGuR8kXjHr'
MAIL_TM_API = 'https://api.mail.tm'
OWNER_NAME = 'Rudra'
GROUP_LINK = 'https://t.me/yourgrouplink'

# === LOGGING ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === UTILITY FUNCTIONS ===
def generate_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_temp_mailbox():
    domain_resp = requests.get(f'{MAIL_TM_API}/domains')
    if domain_resp.status_code != 200:
        return None

    domain = domain_resp.json()['hydra:member'][0]['domain']
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{username}@{domain}"
    password = generate_password()

    create_resp = requests.post(f'{MAIL_TM_API}/accounts', json={
        'address': email,
        'password': password
    })

    if create_resp.status_code == 201:
        return email, password
    else:
        return None

def send_email_via_smtp_dev(to_email: str):
    data = {
        "to": to_email,
        "subject": "Welcome to Temp Email Bot!",
        "text": "This is a test email sent using smtp.dev API. Enjoy your temporary email."
    }
    headers = {
        "Authorization": f"Bearer {SMTP_DEV_API_KEY}"
    }
    response = requests.post("https://api.smtp.dev/send", json=data, headers=headers)
    return response.status_code == 200

# === TELEGRAM COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"👋 Hi {user.mention_html()}!\nUse /getemail to get a temp email.\n\n🔹 Owner: {OWNER_NAME}\n🔹 Group: {GROUP_LINK}",
        reply_markup=ForceReply(selective=True),
    )

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = create_temp_mailbox()
    if result:
        email, password = result
        email_sent = send_email_via_smtp_dev(email)
        note = "✅ Welcome email sent." if email_sent else "⚠️ Failed to send welcome email."
        await update.message.reply_text(
            f"Your temporary email credentials:\nEmail: {email}\nPassword: {password}\n\n{note}"
        )
    else:
        await update.message.reply_text("❌ Failed to create temporary email. Please try again later.")

# === MAIN ===
def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getemail", get_email))
    application.run_polling()

if __name__ == '__main__':
    main()
