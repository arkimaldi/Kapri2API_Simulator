# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

from cfg_loader import CfgLoader


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API = {
        'api_host': '',
        'api_port': 0,
    }

    URL = {
        'url_knpupdaterrxapi': '',
        'url_kxphostproapi': '',
        'url_ktpterminalapi': '',
        'url_jsoterminalapi': '',
        'url_httpterminalapi': '',
        'url_kapriassistapi': '',
    }

    SOCKETIO = {
        'socketio_server_host': '',
        'socketio_server_port': 0
    }

    ROUTES = {
        'routes_imgrepo_dir': ''
    }

    # Syntax:
    # https://docs.python.org/3/library/logging.config.html#logging-config-dictschema
    LOGGING = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'formatter': 'default',
                'class': 'logging.StreamHandler',  # defaults to stderr
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    }

    @staticmethod
    def init_app(app):
        """
        Applies the configuration to the provided Flask app object.
        """
        pass


class TestingConfig(Config):
    TESTING = True

    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # In-memory database

    LOGGING = Config.LOGGING.copy()
    LOGGING.update({
        'root': {
            'level': 'WARNING',
            'handlers': ['console']
        }
    })

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class WaitressConfig(Config):
    SQLALCHEMY_DATABASE_URI = CfgLoader.get('database_uri')

    API = Config.API.copy()
    API.update({
        'api_host': CfgLoader.get('api_host'),
        'api_port': CfgLoader.get('api_port'),
    })

    URL = Config.URL.copy()
    URL.update({
        'url_knpupdaterrxapi': CfgLoader.get('url_knpupdaterrxapi'),
        'url_kxphostproapi': CfgLoader.get('url_kxphostproapi'),
        'url_ktpterminalapi': CfgLoader.get('url_ktpterminalapi'),
        'url_jsoterminalapi': CfgLoader.get('url_jsoterminalapi'),
        'url_httpterminalapi': CfgLoader.get('url_httpterminalapi'),
        'url_kapriassistapi': CfgLoader.get('url_kapriassistapi')
    })

    LOGGING = Config.LOGGING.copy()
    LOGGING.update({
        'root': {
            'level': CfgLoader.get('debug_level'),
            'handlers': ['console']
        }
    })

    SOCKETIO = Config.SOCKETIO.copy()
    SOCKETIO.update({
        'socketio_server_host': CfgLoader.get('socketio_server_host'),
        'socketio_server_port': CfgLoader.get('socketio_server_port')
    })

    ROUTES = Config.ROUTES.copy()
    ROUTES.update({
        'routes_imgrepo_dir': CfgLoader.get('routes_imgrepo_dir')
    })
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = {
    'testing': TestingConfig,
    'waitress': WaitressConfig
}
