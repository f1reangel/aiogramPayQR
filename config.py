from dotenv import load_dotenv
from pathlib import Path
import os

current_dir = Path(__file__).resolve().parent
env_path = current_dir / '.env'

load_dotenv(dotenv_path=env_path)

FIREBASE_SERVICE_ACCOUNT_KEY = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY')
STORAGE_BUCKET_URL = os.getenv('STORAGE_BUCKET_URL')
PUBLIC_LIQPAY_KEY = os.getenv('PUBLIC_LIQPAY_KEY')
PRIVATE_LIQPAY_KEY = os.getenv('PRIVATE_LIQPAY_KEY')
TOKEN_TELEGRAM_BOT = os.getenv('TOKEN_TELEGRAM_BOT')