# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import os
import logging
import logging.config
from flask import Flask
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from appconfig import config
from app.kapri_app import KapriApp
from app.extensions import db, migrate, scheduler, get_migrations_path

# Prefix amb el qual Alembic anomena les taules temporals que crea internament
# quan batch_alter_table necessita recrear una taula.
ALEMBIC_TMP_TABLE_PREFIX = '_alembic_tmp_'


def create_app(config_name, do_start=True) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    logging.config.dictConfig(app.config['LOGGING'])
    logging.info(f"App is configured for '{config_name}'")

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    scheduler.init_app(app)

    kapri_app = KapriApp(app)

    # Register blueprints
    from app.api import api_blueprint
    app.register_blueprint(api_blueprint(kapri_app), url_prefix='/api')

    if do_start:
        with app.app_context():
            from app import cleanup_tasks  # Instantiate jobs from annotated functions
            db_upgrade(app)
            kapri_app.start()
            scheduler.start()
    else:
        logging.info("create_app will not start kapri_app and scheduler")

    @app.shell_context_processor
    def shell_context():
        return {
            'app': app,
            'db': db,
            'scheduler': scheduler,
            'kapri_app': kapri_app,
        }

    return app


def cleanup_orphaned_alembic_tmp_tables():
    """
    Esborra taules '_alembic_tmp_*' que hagin quedat òrfenes d'un intent de
    migració anterior interromput, SEMPRE QUE la taula original
    corresponent encara existeixi.
    """
    with db.engine.begin() as conn:
        inspector = inspect(conn)
        table_names = set(inspector.get_table_names())
        orphaned_tables = [t for t in table_names if t.startswith(ALEMBIC_TMP_TABLE_PREFIX)]

        if not orphaned_tables:
            return

        for temporary_name in orphaned_tables:
            original_name = temporary_name[len(ALEMBIC_TMP_TABLE_PREFIX):]

            if original_name and original_name in table_names:
                logging.error(
                    "WARNING - db_upgrade: found orphaned temporary table '%s', and the "
                    "original table '%s' still exists -- dropping the "
                    "temporary table.",
                    temporary_name, original_name,
                )
                conn.execute(text(f'DROP TABLE "{temporary_name}"'))
            else:
                raise RuntimeError(
                    f"db_upgrade: temporary table '{temporary_name}' exists "
                    f"without its corresponding original table."
                )


def db_upgrade(app):
    # neteja defensiva abans de migrar: si un intent anterior va quedar
    # interromput a mig d'una recreació de taula, cal esborrar la taula
    # temporal òrfena o Alembic tornarà a fallar de manera permanent.
    cleanup_orphaned_alembic_tmp_tables()

    migrations_path = get_migrations_path()
    alembic_ini_path = os.path.join(migrations_path, 'alembic.ini')
    alembic_cfg = Config(alembic_ini_path)  # Specify the path to your alembic.ini file
    alembic_cfg.set_main_option('script_location', migrations_path)

    command.upgrade(alembic_cfg, 'head')
    # com que alembic altera la configuració del logger la restaurem segons app.config
    logging.config.dictConfig(app.config['LOGGING'])