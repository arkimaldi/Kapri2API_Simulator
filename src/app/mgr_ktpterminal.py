# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import time
import inspect
import json
import threading
import logging

from app.global_consts import GlobalConsts
from k_check import KCheck
from app.db_models import NanoConfiguration
from app.extensions import db
from app.post_woman import PostWoman


class MgrKtpterminal:

    class TerminalException(Exception):
        def __init__(self, message=''):
            # Call the base class constructor with the parameters it needs
            super(MgrKtpterminal.TerminalException, self).__init__(message)

    def __init__(self, app, mgr_hardware_info ):
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

            # Parameters Ktp
            sNetworkId = nano_configuration_1_qry.ktp_network_id
            sAes256Key = nano_configuration_1_qry.ktp_aes256
            result = self.send_and_receive(
                {
                    'sNetworkId': sNetworkId,
                    'sAes256Key':sAes256Key
                },
                '/api/parameters/ktpcom/write'
            )
            sEUI64 = self.mgr_hardware_info.get('sEUI64')
            ucModelNo = GlobalConsts.get('const_my_uc_model_no')
            sName = GlobalConsts.get('const_my_sname')
            sVersion = GlobalConsts.get('const_my_version')
            sDescription = nano_configuration_1_qry.terminal_description
            result = self.send_and_receive(
                {
                    'sEUI64': sEUI64,
                    'ucModelNo': ucModelNo,
                    'sName': sName,
                    'sVersion': sVersion,
                    'sDescription': sDescription},
                '/api/parameters/ktpterminal/write'
            )
            logging.debug(f"api/parameters/ktpterminal/write: sEUI64: {sEUI64}, ucModelNo: {ucModelNo}, sName: {sName}, sVersion: {sVersion}, sDescription: {sDescription} ucRet = {result['msgArg']['ucRet']}")

            self.send_and_receive({'msgType': 'cmd_stop_terminal', 'msgArg': {}})
            self.b_opened = False
            logging.debug('cmd_stop_terminal')
            if not nano_configuration_1_qry.ktp_interface:
                raise MgrKtpterminal.TerminalException('KTP_Interface_False')
            time.sleep(1)
            if nano_configuration_1_qry.ktp_server_client_mode == 'Server':
                if nano_configuration_1_qry.ktp_udp_detect:       # Server i UDP
                    logging.debug("# Server i UDP")
                    self.send_and_receive(
                        {
                            'msgType': 'cmd_start_terminal_as_server',
                            'msgArg': {
                                'uiUdpBeaconLocalPort': nano_configuration_1_qry.ktp_udp_port,
                                'uiTerminalServerLocalPort':65432
                            }
                        }
                    )
                    self.b_opened = True
                    logging.debug('cmd_start_terminal_as_server, UDP')
                else:                              # Server i No UDP
                    logging.debug("# Server i No UDP")
                    self.send_and_receive(
                        {'msgType': 'cmd_start_terminal_as_server',
                         'msgArg': {
                             'uiUdpBeaconLocalPort': 0,
                             'uiTerminalServerLocalPort':65432
                         }
                         }
                    )
                    self.b_opened = True
                    logging.debug('cmd_start_terminal_as_server, No UDP')

            else:    # 'Client'
                if nano_configuration_1_qry.ktp_udp_detect:       # Client i UDP
                    logging.debug("# Client i  UDP")
                    result = self.send_and_receive(
                        {
                            'msgType': 'cmd_start_terminal_as_client',
                            'msgArg': {
                                'uiUdpBeaconLocalPort': nano_configuration_1_qry.ktp_udp_port
                            }
                        }
                    )
                    logging.debug(f"cmd_start_terminal_as_client uiUdpBeaconLocalPort: {nano_configuration_1_qry.ktp_udp_port}")
                    self.b_opened = True
                    logging.debug('cmd_start_terminal_as_client, UDP')
                    time.sleep(1)

                else:                              # Client i No UDP
                    logging.debug("# Client i  No UDP")
                    self.send_and_receive(
                        {
                            'msgType': 'cmd_start_terminal_as_client',
                            'msgArg': {'uiUdpBeaconLocalPort': 0}
                        }
                    )
                    self.b_opened = True
                    logging.debug('cmd_start_terminal_as_client, No UDP')
                    if nano_configuration_1_qry.ktp_remote_server_ip_1 != "":
                        try:
                            uiIpPort = KCheck.integerInInterval(nano_configuration_1_qry.ktp_remote_server_port_1, 1025, 65535)
                        except Exception as e:
                            uiIpPort = 65431
                        self.send_and_receive(
                            {
                                'msgType': 'cmd_manually_add_host_server',
                                'msgArg': {
                                    'sIpAddress': nano_configuration_1_qry.ktp_remote_server_ip_1,
                                    'uiIpPort': uiIpPort
                                }
                            }
                        )
                    if nano_configuration_1_qry.ktp_remote_server_ip_2 != "":
                        try:
                            uiIpPort = KCheck.integerInInterval(nano_configuration_1_qry.ktp_remote_server_port_2, 1025, 65535)
                        except Exception as e:
                            uiIpPort = 65431
                        self.send_and_receive(
                            {
                                'msgType': 'cmd_manually_add_host_server',
                                'msgArg': {
                                    'sIpAddress': nano_configuration_1_qry.ktp_remote_server_ip_2,
                                    'uiIpPort': uiIpPort
                                }
                            }
                        )
        except MgrKtpterminal.TerminalException as e:
            self.b_opened = False
            logging.info(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        except Exception as e:
            self.b_opened = False
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            db.session.close()

    def get_version(self):
        try:
            ktp_message_out = self.send_and_receive({'msgType': 'cmd_get_version', 'msgArg': {}})
            return ktp_message_out['msgArg']['sVersion']
        except Exception as e:
            return None

    def send_and_receive(self, my_dictio, leading_url='/api/interpreter'):
        # Farem servir aquesta funció per totes les crides API al KtpTerminalProAPI
        # El segon paramatre especificarà la url completa
        # per defecte es url_ktpterminalapi+'/api/interpreter'
        try:
            my_url = self.app.config['URL']['url_ktpterminalapi'] + leading_url
            result = PostWoman.send_post(my_url, my_dictio)
            return result
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return { 'Error': str(e) }

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