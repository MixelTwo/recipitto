import os

from bafser import AppConfig, randstr
from sqlalchemy.orm import Session

from data.user import User


def init_db(db_sess: Session, config: AppConfig):
    admin = User.get_by_login(db_sess, "admin")
    if admin:
        admin.set_password(os.environ.get("ADMIN_PASSWORD", randstr(16)))
        db_sess.commit()

    db_sess.commit()
