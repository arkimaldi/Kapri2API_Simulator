# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import os
import toml

import constants
from k_check import KCheck


class CfgLoader:
    cfg_dict = {
        # from config
        # [debug]
        'debug_level': 'ERROR',
        # [api]
        'api_host': '0.0.0.0',
        'api_port': 0,
        # [url]
        'url_knpupdaterrxapi': 'http://127.0.0.1:9442',
        'url_kxphostproapi': 'http://127.0.0.1:9443',
        'url_ktpterminalapi': 'http://127.0.0.1:11443',
        'url_jsoterminalapi': 'http://127.0.0.1:9444',
        'url_httpterminalapi': 'http://127.0.0.1:9445',
        'url_kapriassistapi': 'http://127.0.0.1:45775',
        # [socketio]
        'socketio_server_host': '0.0.0.0',
        'socketio_server_port': 0,
        # [database]
        'database_uri': 'sqlite:///dev.sqlite',
        # [routes]
        'routes_imgrepo_dir': constants.IMGREPO_DIRNAME_DEFAULT
    }

    @staticmethod
    def set(key, value):
        if key not in CfgLoader.cfg_dict.keys():
            raise
        CfgLoader.cfg_dict[key] = value

    @staticmethod
    def get(key):
        return CfgLoader.cfg_dict[key]


    @staticmethod
    def load_cfg_file(config_file_route):
        with open(config_file_route, 'r') as f:
            cfg_toml_dict = toml.loads(f.read())

            # debug_level
            cfg_debug = cfg_toml_dict.get('debug', {})
            if 'debug_level' in cfg_debug.keys():
                cfg_DEBUG_LEVEL = KCheck.elementInList(cfg_debug['debug_level'].strip().upper(),
                                                       ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
                CfgLoader.set('debug_level', cfg_DEBUG_LEVEL)

            # API
            cfg_api = cfg_toml_dict.get('api', {})
            if 'api_host' in cfg_api.keys():
                CfgLoader.set('api_host', cfg_api['api_host'].strip())
            if 'api_port' in cfg_api.keys():
                CfgLoader.set('api_port', str(KCheck.integerInInterval(cfg_api['api_port'], 1025, 65535)))

            # DATABASE
            cfg_database = cfg_toml_dict.get('database', {})
            if 'database_uri' in cfg_database.keys():
                cfg_DATABASE_URI = cfg_database['database_uri'].strip()
                CfgLoader.set('database_uri', cfg_DATABASE_URI)

            # URL
            cfg_url = cfg_toml_dict.get('url', {})
            if 'url_knpupdaterrxapi' in cfg_url.keys():
                CfgLoader.set('url_knpupdaterrxapi', cfg_url['url_knpupdaterrxapi'].strip())
            if 'url_kxphostproapi' in cfg_url.keys():
                CfgLoader.set('url_kxphostproapi', cfg_url['url_kxphostproapi'].strip())
            if 'url_ktpterminalapi' in cfg_url.keys():
                CfgLoader.set('url_ktpterminalapi', cfg_url['url_ktpterminalapi'].strip())
            if 'url_jsoterminalapi' in cfg_url.keys():
                CfgLoader.set('url_jsoterminalapi', cfg_url['url_jsoterminalapi'].strip())
            if 'url_httpterminalapi' in cfg_url.keys():
                CfgLoader.set('url_httpterminalapi', cfg_url['url_httpterminalapi'].strip())
            if 'url_kapriassistapi' in cfg_url.keys():
                CfgLoader.set('url_kapriassistapi', cfg_url['url_kapriassistapi'].strip())

            # SOCKETIO
            cfg_socketio = cfg_toml_dict.get('socketio', {})
            if 'socketio_server_host' in cfg_socketio.keys():
                CfgLoader.set('socketio_server_host', cfg_socketio['socketio_server_host'].strip())
            if 'socketio_server_port' in cfg_socketio.keys():
                CfgLoader.set('socketio_server_port', str(KCheck.integerInInterval(cfg_socketio['socketio_server_port'], 1025, 65535)))

            # ROUTES
            cfg_routes = cfg_toml_dict.get('routes', {})
            if 'routes_imgrepo_dir' in cfg_routes.keys():
                CfgLoader.set('routes_imgrepo_dir', cfg_routes['routes_imgrepo_dir'])

            # - comprovacions addicionals sobre la configuració resultant
            if not os.path.isdir(CfgLoader.get('routes_imgrepo_dir')):
                raise Exception('Invalid imgrepo folder')
