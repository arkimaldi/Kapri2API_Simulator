# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import time
import inspect
import json
import threading
import logging

from k_check import KCheck
from app.db_models import NanoConfiguration
from app.extensions import db
from app.post_woman import PostWoman


class MgrJsoterminal:

    class TerminalException(Exception):
        def __init__(self, message=''):
            # Call the base class constructor with the parameters it needs
            super(MgrJsoterminal.TerminalException, self).__init__(message)

    def __init__(self, app):
        self.app = app
        #
        self.b_opened = False

    def start(self):
        try:
            nano_configuration_1_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 1).first()
            if nano_configuration_1_qry is None:
                db.session.close()
                return
            self.send_and_receive({'msgType': 'cmd_stop_terminal', 'msgArg': {}})
            self.b_opened = False
            logging.debug('cmd_stop_terminal')
            if not nano_configuration_1_qry.jso_interface:
                raise MgrJsoterminal.TerminalException('JSO_Interface_False')
            time.sleep(1)
            if nano_configuration_1_qry.jso_server_client_mode == 'Server':
                logging.debug("# Server ")
                self.send_and_receive(
                    {
                        'msgType': 'cmd_start_terminal_as_server',
                        'msgArg': {'uiTerminalServerLocalPort': 65442}
                    }
                )
                self.b_opened = True
                logging.debug('cmd_start_terminal_as_server')
            else:  # 'Client'
                logging.debug("# Client ")
                self.send_and_receive({'msgType': 'cmd_start_terminal_as_client', 'msgArg': {}})
                self.b_opened = True
                logging.debug('cmd_start_terminal_as_client')
                if nano_configuration_1_qry.jso_remote_server_ip_1 != "":
                    try:
                        uiIpPort = KCheck.integerInInterval(nano_configuration_1_qry.jso_remote_server_port_1, 1025, 65535)
                    except Exception as e:
                        uiIpPort = 65441
                    self.send_and_receive(
                        {
                            'msgType': 'cmd_manually_add_host_server',
                            'msgArg': {
                                'sIpAddress': nano_configuration_1_qry.jso_remote_server_ip_1,
                                'uiIpPort': uiIpPort
                            }
                        }
                    )
                if nano_configuration_1_qry.jso_remote_server_ip_2 != "":
                    try:
                        uiIpPort = KCheck.integerInInterval(nano_configuration_1_qry.jso_remote_server_port_2, 1025, 65535)
                    except Exception as e:
                        uiIpPort = 65441
                    self.send_and_receive(
                        {
                            'msgType': 'cmd_manually_add_host_server',
                            'msgArg': {
                                'sIpAddress': nano_configuration_1_qry.jso_remote_server_ip_2,
                                'uiIpPort': uiIpPort
                            }
                        }
                    )
        except MgrJsoterminal.TerminalException as e:
            self.b_opened = False
            logging.info(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        except Exception as e:
            self.b_opened = False
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            db.session.close()

    def get_version(self):
        try:
            jso_message_out = self.send_and_receive({'msgType': 'cmd_get_version', 'msgArg': {}})
            return jso_message_out['msgArg']['sVersion']
        except Exception as e:
            return None

    def send_and_receive(self, my_dictio, leading_url='/api/interpreter'):
        # Farem servir aquesta funció per totes les crides API al Jso Terminal
        # El segon paramatre especificarà la url completa
        # per defecte es cfg_api_jsoterminalapiurl+'/api/interpreter'
        try:
            my_url = self.app.config['URL']['url_jsoterminalapi'] + leading_url
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
        self.send_and_receive(my_dictio)


