# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import os
import sys
from flask_apscheduler import APScheduler
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

def get_migrations_path():
    if hasattr(sys, '_MEIPASS'):
        migrations_path = os.path.join(sys._MEIPASS, 'src', 'migrations')  # When compiled
    else:
        migrations_path = os.path.join(os.getcwd(), 'src', 'migrations')  # For development
    return migrations_path


db = SQLAlchemy()

migrations_path = get_migrations_path()
migrate = Migrate(directory=migrations_path)

scheduler = APScheduler()
