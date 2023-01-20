from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    MNEM = os.environ.get('MNEM')
    ONBOARD_FILEPATH = os.environ.get('ONBOARD_FILEPATH')
    FUNDME_FILEPATH = os.environ.get('FUNDME_FILEPATH')
    SEND_TO_ADDRESS = os.environ.get('SEND_TO_ADDRESS')
    NEW_ACCOUNT_AUTH = os.environ.get('NEW_ACCOUNT_AUTH')
    