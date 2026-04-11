import os
import sys

from bafser import AppConfig, create_app
from dotenv import load_dotenv

from utils.init_db import init_db
from utils.init_db_dev import init_db_dev

load_dotenv()

app, run = create_app(
    __name__,
    AppConfig(
        MESSAGE_TO_FRONTEND="",
        DEV_MODE="dev" in sys.argv or os.environ.get("DEV", "0") == "1",
        DELAY_MODE="delay" in sys.argv or os.environ.get("DELAY", "0") == "1",
    ),
)

run(__name__ == "__main__", init_db, init_db_dev)
