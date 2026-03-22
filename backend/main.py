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
        DEV_MODE="dev" in sys.argv,
        DELAY_MODE="delay" in sys.argv,
    ),
)

run(__name__ == "__main__", init_db, init_db_dev)
