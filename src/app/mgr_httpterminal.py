# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import time
import inspect
import json
import threading
import logging

from app.db_models import NanoConfiguration
from app.extensions import db
from app.post_woman import PostWoman


class Mgr_Httpterminal:

    class TerminalException(Exception):
        def __init__(self, message=''):
            # Call the base class constructor with the parameters it needs
            super(Mgr_Httpterminal.TerminalException, self).__init__(message)

    def __init__(self, app, mgr_hardware_info):
        self.app = app
        self.mgr_hardware_info = mgr_hardware_info
        #
        self.b_opened = False

    def start(self):
        try:
            nano_configuration_1_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 1).first()
            if nano_configuration_1_qry is None:
                db.session.close()
                return
            self.send_and_receive({'msgType': 'cmd_stop_terminal', 'msgArg': {'s_i_s': '0qtp%kf#25'}})
            self.b_opened = False
            logging.debug('cmd_stop_terminal')
            if not nano_configuration_1_qry.http_interface:
                raise Mgr_Httpterminal.TerminalException('HTTP_Interface_False')
            time.sleep(1)
            self.send_and_receive(
                {
                    'msgType': 'cmd_start_terminal',
                    'msgArg': {
                        's_i_s': '0qtp%kf#25',
                        'sSocketioHostServer': nano_configuration_1_qry.http_socketio_server_host,
                        'uiSocketioPortServer': nano_configuration_1_qry.http_socketio_server_port,
                        'sSocketioEventTag': 'http_sio_event'
                    }
                }
            )
            self.b_opened = True
            logging.debug('cmd_start_terminal')
        except Mgr_Httpterminal.TerminalException as e:
            self.b_opened = False
            logging.info(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        except Exception as e:
            self.b_opened = False
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            db.session.close()

    def get_version(self):
        try:
            http_message_out = self.send_and_receive({'msgType': 'cmd_get_version', 'msgArg': {'s_i_s': '0qtp%kf#25'}})
            return http_message_out['msgArg']['sVersion']
        except Exception as e:
            return None

    def send_and_receive(self, my_dictio, leading_url='/api/interpreter'):
        # Farem servir aquesta funció per totes les crides API al Http Terminal
        # El segon paramatre especificarà la url completa
        # per defecte es url_httpterminalapi+'/api/interpreter'
        try:
            my_url = self.app.config['URL']['url_httpterminalapi'] + leading_url
            result = PostWoman.send_post(my_url, my_dictio)
            return result
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return {'Error': str(e)}

    def manage_event(self, my_dictio):
        try:
            if self.b_opened:
                dictio = json.loads(json.dumps(my_dictio))
                event_raiser_thread = threading.Thread(target=self.event_raiser_thread_task, args=(dictio,))
                event_raiser_thread.daemon = True
                event_raiser_thread.start()
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def event_raiser_thread_task(self, my_dictio):
        try:
            my_dictio['msgArg']['s_i_s'] = '0qtp%kf#25'
            my_dictio['msgArg']['sEUI64'] = self.mgr_hardware_info.get('sEUI64')
            self.send_and_receive(my_dictio)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
