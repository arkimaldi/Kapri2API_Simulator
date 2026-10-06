# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
import socket
import json
import pytz
import logging

from k_check import KCheck
from app.global_consts import GlobalConsts
from app.ktp_ret import KtpRet
from app.extensions import db
from app.db_models import NanoConfiguration
from app.utilities import Utils


class MgrConfigNano:

    def __init__(self, app, mgr_kapriassist, mgr_interface_global, mgr_ktpterminal, mgr_jsoterminal, mgr_httpterminal, mgr_cloudterminal, mgr_semi_offline, mgr_scankey, mgr_kybmgr_configurer):
        self.app = app
        self.mgr_kapriassist = mgr_kapriassist
        self.mgr_interface_global = mgr_interface_global
        self.mgr_ktpterminal = mgr_ktpterminal
        self.mgr_jsoterminal = mgr_jsoterminal
        self.mgr_httpterminal = mgr_httpterminal
        self.mgr_cloudterminal = mgr_cloudterminal
        self.mgr_semi_offline = mgr_semi_offline
        self.mgr_scankey = mgr_scankey
        self.mgr_kybmgr_configurer = mgr_kybmgr_configurer

    def write_future(self, dict_params):
        param_failed = None
        try:
            # La configuració amb id=2 és la futura un cop reinicialitzi el sistema
            nano_configuration_2_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 2).first()
            if nano_configuration_2_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION
            if dict_params.get('terminal_description') is not None:
                param_failed = 'terminal_description'
                nano_configuration_2_qry.terminal_description = KCheck.stringLenInInterval(
                    dict_params['terminal_description'],
                    GlobalConsts.get('const_terminal_description_lenmin'),
                    GlobalConsts.get('const_terminal_description_size')
                )
            if dict_params.get('rtc_local_timezone') is not None:
                param_failed = 'rtc_local_timezone'
                nano_configuration_2_qry.rtc_local_timezone = KCheck.elementInList(dict_params['rtc_local_timezone'], pytz.all_timezones)
            if dict_params.get('network_ip_address') is not None:
                param_failed = 'network_ip_address'
                socket.inet_aton(dict_params['network_ip_address'])
                nano_configuration_2_qry.network_ip_address = dict_params['network_ip_address']
            if dict_params.get('network_bits_mask') is not None:
                param_failed = 'network_bits_mask'
                nano_configuration_2_qry.network_bits_mask = KCheck.integerInInterval(dict_params['network_bits_mask'], 8, 30)
            if dict_params.get('network_ip_router') is not None:
                param_failed = 'network_ip_router'
                socket.inet_aton(dict_params['network_ip_router'])
                nano_configuration_2_qry.network_ip_router = dict_params['network_ip_router']
            if dict_params.get('network_dhcp_mode') is not None:
                param_failed = 'network_dhcp_mode'
                KCheck.stringLenInInterval(dict_params['network_dhcp_mode'], 1, 255)
                nano_configuration_2_qry.network_dhcp_mode = KCheck.elementInList(
                    dict_params['network_dhcp_mode'],
                    GlobalConsts.get('const_network_dhcp_mode_values')
                )
            if dict_params.get('wlan_enabled') is not None:
                param_failed = 'wlan_enabled'
                nano_configuration_2_qry.wlan_enabled = KCheck.booleanValue(dict_params['wlan_enabled'])
            if dict_params.get('wlan_ssid') is not None:
                param_failed = 'wlan_ssid'
                nano_configuration_2_qry.wlan_ssid = KCheck.stringLenInInterval(
                    dict_params['wlan_ssid'].strip(),
                    GlobalConsts.get('const_wlan_ssid_lenmin'),
                    GlobalConsts.get('const_wlan_ssid_size')
                )
            if dict_params.get('wlan_password') is not None:
                param_failed = 'wlan_password'
                nano_configuration_2_qry.wlan_password = KCheck.stringLenInInterval(
                    dict_params['wlan_password'].strip(),
                    GlobalConsts.get('const_wlan_password_lenmin'),
                    GlobalConsts.get('const_wlan_password_size')
                )
            if dict_params.get('interface_ins_pwd') is not None:
                param_failed = 'interface_ins_pwd'
                nano_configuration_2_qry.interface_ins_pwd = KCheck.stringLenInInterval(
                    dict_params['interface_ins_pwd'],
                    GlobalConsts.get('const_interface_ins_pwd_lenmin'),
                    GlobalConsts.get('const_interface_ins_pwd_size')
                )
            if dict_params.get('ktp_interface') is not None:
                param_failed = 'ktp_interface'
                nano_configuration_2_qry.ktp_interface = KCheck.booleanValue(dict_params['ktp_interface'])
            if dict_params.get('jso_interface') is not None:
                param_failed = 'jso_interface'
                nano_configuration_2_qry.jso_interface = KCheck.booleanValue(dict_params['jso_interface'])
            if dict_params.get('http_interface') is not None:
                param_failed = 'http_interface'
                nano_configuration_2_qry.http_interface = KCheck.booleanValue(dict_params['http_interface'])
            if dict_params.get('cloud_interface') is not None:
                param_failed = 'cloud_interface'
                nano_configuration_2_qry.cloud_interface = KCheck.booleanValue(dict_params['cloud_interface'])
            if dict_params.get('ktp_server_client_mode') is not None:
                param_failed = 'ktp_server_client_mode'
                nano_configuration_2_qry.ktp_server_client_mode = KCheck.elementInList(
                    dict_params['ktp_server_client_mode'],
                    GlobalConsts.get('const_ktp_server_client_mode_values')
                )
            if dict_params.get('ktp_remote_server_ip_1') is not None:
                param_failed = 'ktp_remote_server_ip_1'
                if dict_params['ktp_remote_server_ip_1'] != '':
                    socket.inet_aton(dict_params['ktp_remote_server_ip_1'])
                nano_configuration_2_qry.ktp_remote_server_ip_1 = dict_params['ktp_remote_server_ip_1']
            if dict_params.get('ktp_remote_server_ip_2') is not None:
                param_failed = 'ktp_remote_server_ip_2'
                if dict_params['ktp_remote_server_ip_2'] != '':
                    socket.inet_aton(dict_params['ktp_remote_server_ip_2'])
                nano_configuration_2_qry.ktp_remote_server_ip_2 = dict_params['ktp_remote_server_ip_2']
            if dict_params.get('ktp_remote_server_port_1') is not None:
                param_failed = 'ktp_remote_server_port_1'
                nano_configuration_2_qry.ktp_remote_server_port_1 = KCheck.integerInInterval(dict_params['ktp_remote_server_port_1'], 1025, 65535)
            if dict_params.get('ktp_remote_server_port_2') is not None:
                param_failed = 'ktp_remote_server_port_2'
                nano_configuration_2_qry.ktp_remote_server_port_2 = KCheck.integerInInterval(dict_params['ktp_remote_server_port_2'], 1025, 65535)
            if dict_params.get('ktp_udp_detect') is not None:
                param_failed = 'ktp_udp_detect'
                nano_configuration_2_qry.ktp_udp_detect = KCheck.booleanValue(dict_params['ktp_udp_detect'])
            if dict_params.get('ktp_udp_port') is not None:
                param_failed = 'ktp_udp_port'
                nano_configuration_2_qry.ktp_udp_port = KCheck.integerInInterval(dict_params['ktp_udp_port'], 1025, 65535)
            if dict_params.get('ktp_network_id') is not None:
                param_failed = 'ktp_network_id'
                nano_configuration_2_qry.ktp_network_id = KCheck.stringLenInInterval(
                    dict_params['ktp_network_id'],
                    GlobalConsts.get('const_ktp_network_id_lenmin'),
                    GlobalConsts.get('const_ktp_network_id_size')
                )
            if dict_params.get('ktp_aes256') is not None:
                param_failed = 'ktp_aes256'
                if Utils.bChkHexString(dict_params['ktp_aes256'], GlobalConsts.get('const_ktp_aes256_size')):
                    nano_configuration_2_qry.ktp_aes256 = dict_params['ktp_aes256']
                else:
                    raise Exception('Invalid ktp_aes256')
            if dict_params.get('jso_server_client_mode') is not None:
                param_failed = 'jso_server_client_mode'
                nano_configuration_2_qry.jso_server_client_mode = KCheck.elementInList(
                    dict_params['jso_server_client_mode'],
                    GlobalConsts.get('const_jso_server_client_mode_values')
                )
            if dict_params.get('jso_remote_server_ip_1') is not None:
                param_failed = 'jso_remote_server_ip_1'
                if dict_params['jso_remote_server_ip_1'] != '':
                    socket.inet_aton(dict_params['jso_remote_server_ip_1'])
                nano_configuration_2_qry.jso_remote_server_ip_1 = dict_params['jso_remote_server_ip_1']
            if dict_params.get('jso_remote_server_ip_2') is not None:
                param_failed = 'jso_remote_server_ip_2'
                if dict_params['jso_remote_server_ip_2'] != '':
                    socket.inet_aton(dict_params['jso_remote_server_ip_2'])
                nano_configuration_2_qry.jso_remote_server_ip_2 = dict_params['jso_remote_server_ip_2']
            if dict_params.get('jso_remote_server_port_1') is not None:
                param_failed = 'jso_remote_server_port_1'
                nano_configuration_2_qry.jso_remote_server_port_1 = KCheck.integerInInterval(dict_params['jso_remote_server_port_1'], 1025, 65535)
            if dict_params.get('jso_remote_server_port_2') is not None:
                param_failed = 'jso_remote_server_port_2'
                nano_configuration_2_qry.jso_remote_server_port_2 = KCheck.integerInInterval(dict_params['jso_remote_server_port_2'], 1025, 65535)
            if dict_params.get('http_socketio_server_host') is not None:
                param_failed = 'http_socketio_server_host'
                if dict_params['http_socketio_server_host'] != '':
                    socket.inet_aton(dict_params['http_socketio_server_host'])
                nano_configuration_2_qry.http_socketio_server_host = dict_params['http_socketio_server_host']
            if dict_params.get('http_socketio_server_port') is not None:
                param_failed = 'http_socketio_server_port'
                nano_configuration_2_qry.http_socketio_server_port = KCheck.integerInInterval(dict_params['http_socketio_server_port'], 1025, 65535)
            if dict_params.get('cloud_remote_server_url') is not None:
                param_failed = 'cloud_remote_server_url'
                if not KCheck.validate_url(dict_params['cloud_remote_server_url']):
                    raise
                nano_configuration_2_qry.cloud_remote_server_url = KCheck.stringLenInInterval(
                    dict_params['cloud_remote_server_url'],
                    GlobalConsts.get('const_cloud_remote_server_url_lenmin'),
                    GlobalConsts.get('const_cloud_remote_server_url_size')
                )
            if dict_params.get('cloud_remote_server_token') is not None:
                param_failed = 'cloud_remote_server_token'
                nano_configuration_2_qry.cloud_remote_server_token = KCheck.stringLenInInterval(
                    dict_params['cloud_remote_server_token'],
                    GlobalConsts.get('const_cloud_remote_server_token_lenmin'),
                    GlobalConsts.get('const_cloud_remote_server_token_size')
                )
            if dict_params.get('cloud_allowed_events') is not None:
                param_failed = 'cloud_allowed_events'
                nano_configuration_2_qry.cloud_allowed_events = MgrConfigNano.check_cloud_allowed_events(dict_params['cloud_allowed_events'])
                KCheck.stringLenInInterval(
                    nano_configuration_2_qry.cloud_allowed_events,
                    GlobalConsts.get('const_cloud_allowed_events_lenmin'),
                    GlobalConsts.get('const_cloud_allowed_events_size')
                )
            if dict_params.get('cloud_keep_alive_timeout') is not None:
                param_failed = 'cloud_keep_alive_timeout'
                nano_configuration_2_qry.cloud_keep_alive_timeout = KCheck.integerInInterval(dict_params['cloud_keep_alive_timeout'], 1, 24*3600)
            if dict_params.get('cloud_busy_relay') is not None:
                param_failed = 'cloud_busy_relay'
                nano_configuration_2_qry.cloud_busy_relay = KCheck.integerInInterval(dict_params['cloud_busy_relay'], -1, 2)
            if dict_params.get('semi_offline_mode_enabled') is not None:
                param_failed = 'semi_offline_mode_enabled'
                nano_configuration_2_qry.semi_offline_mode_enabled = KCheck.booleanValue(dict_params.get('semi_offline_mode_enabled'))
            if dict_params.get('semi_offline_keep_alive_timeout') is not None:
                param_failed = 'semi_offline_keep_alive_timeout'
                nano_configuration_2_qry.semi_offline_keep_alive_timeout = KCheck.integerInInterval(dict_params['semi_offline_keep_alive_timeout'], 1, 24*3600)
            if dict_params.get('semi_offline_on_semi_offline_mode_enter_batch') is not None:
                param_failed = 'semi_offline_on_semi_offline_mode_enter_batch'
                if dict_params.get('semi_offline_on_semi_offline_mode_enter_batch') == '':
                    nano_configuration_2_qry.semi_offline_on_semi_offline_mode_enter_batch = ''
                else:
                    nano_configuration_2_qry.semi_offline_on_semi_offline_mode_enter_batch = json.dumps(json.loads(dict_params.get('semi_offline_on_semi_offline_mode_enter_batch')))
                    KCheck.stringLenInInterval(
                        nano_configuration_2_qry.semi_offline_on_semi_offline_mode_enter_batch,
                        GlobalConsts.get('const_semi_offline_batch_lenmin'),
                        GlobalConsts.get('const_semi_offline_batch_size')
                    )
            if dict_params.get('semi_offline_on_usrtimer_elapsed_batch') is not None:
                param_failed = 'semi_offline_on_usrtimer_elapsed_batch'
                if dict_params.get('semi_offline_on_usrtimer_elapsed_batch') == '':
                    nano_configuration_2_qry.semi_offline_on_usrtimer_elapsed_batch = ''
                else:
                    nano_configuration_2_qry.semi_offline_on_usrtimer_elapsed_batch = json.dumps(json.loads(dict_params.get('semi_offline_on_usrtimer_elapsed_batch')))
                    KCheck.stringLenInInterval(
                        nano_configuration_2_qry.semi_offline_on_usrtimer_elapsed_batch,
                        GlobalConsts.get('const_semi_offline_batch_lenmin'),
                        GlobalConsts.get('const_semi_offline_batch_size')
                    )
            if dict_params.get('semi_offline_on_mifare_track_batch') is not None:
                param_failed = 'semi_offline_on_mifare_track_batch'
                if dict_params.get('semi_offline_on_mifare_track_batch') == '':
                    nano_configuration_2_qry.semi_offline_on_mifare_track_batch = ''
                else:
                    nano_configuration_2_qry.semi_offline_on_mifare_track_batch = json.dumps(json.loads(dict_params.get('semi_offline_on_mifare_track_batch')))
                    KCheck.stringLenInInterval(
                        nano_configuration_2_qry.semi_offline_on_mifare_track_batch,
                        GlobalConsts.get('const_semi_offline_batch_lenmin'),
                        GlobalConsts.get('const_semi_offline_batch_size')
                    )
            if dict_params.get('semi_offline_on_ttl_track_batch') is not None:
                param_failed = 'semi_offline_on_ttl_track_batch'
                if dict_params.get('semi_offline_on_ttl_track_batch') == '':
                    nano_configuration_2_qry.semi_offline_on_ttl_track_batch = ''
                else:
                    nano_configuration_2_qry.semi_offline_on_ttl_track_batch = json.dumps(json.loads(dict_params.get('semi_offline_on_ttl_track_batch')))
                    KCheck.stringLenInInterval(
                        nano_configuration_2_qry.semi_offline_on_ttl_track_batch,
                        GlobalConsts.get('const_semi_offline_batch_lenmin'),
                        GlobalConsts.get('const_semi_offline_batch_size')
                    )
            if dict_params.get('semi_offline_on_fim_finger_batch') is not None:
                param_failed = 'semi_offline_on_fim_finger_batch'
                if dict_params.get('semi_offline_on_fim_finger_batch') == '':
                    nano_configuration_2_qry.semi_offline_on_fim_finger_batch = ''
                else:
                    nano_configuration_2_qry.semi_offline_on_fim_finger_batch = json.dumps(json.loads(dict_params.get('semi_offline_on_fim_finger_batch')))
                    KCheck.stringLenInInterval(
                        nano_configuration_2_qry.semi_offline_on_fim_finger_batch,
                        GlobalConsts.get('const_semi_offline_batch_lenmin'),
                        GlobalConsts.get('const_semi_offline_batch_size')
                    )
            if dict_params.get('semi_offline_on_sfm_finger_batch') is not None:
                param_failed = 'semi_offline_on_sfm_finger_batch'
                if dict_params.get('semi_offline_on_sfm_finger_batch') == '':
                    nano_configuration_2_qry.semi_offline_on_sfm_finger_batch = ''
                else:
                    nano_configuration_2_qry.semi_offline_on_sfm_finger_batch = json.dumps(json.loads(dict_params.get('semi_offline_on_sfm_finger_batch')))
                    KCheck.stringLenInInterval(
                        nano_configuration_2_qry.semi_offline_on_sfm_finger_batch,
                        GlobalConsts.get('const_semi_offline_batch_lenmin'),
                        GlobalConsts.get('const_semi_offline_batch_size')
                    )
            if dict_params.get('semi_offline_on_keyboard_echo_batch') is not None:
                param_failed = 'semi_offline_on_keyboard_echo_batch'
                if dict_params.get('semi_offline_on_keyboard_echo_batch') == '':
                    nano_configuration_2_qry.semi_offline_on_keyboard_echo_batch = ''
                else:
                    nano_configuration_2_qry.semi_offline_on_keyboard_echo_batch = json.dumps(json.loads(dict_params.get('semi_offline_on_keyboard_echo_batch')))
                    KCheck.stringLenInInterval(
                        nano_configuration_2_qry.semi_offline_on_keyboard_echo_batch,
                        GlobalConsts.get('const_semi_offline_batch_lenmin'),
                        GlobalConsts.get('const_semi_offline_batch_size')
                    )
            if dict_params.get('semi_offline_on_uart_receive_batch') is not None:
                param_failed = 'semi_offline_on_uart_receive_batch'
                if dict_params.get('semi_offline_on_uart_receive_batch') == '':
                    nano_configuration_2_qry.semi_offline_on_uart_receive_batch = ''
                else:
                    nano_configuration_2_qry.semi_offline_on_uart_receive_batch = json.dumps(json.loads(dict_params.get('semi_offline_on_uart_receive_batch')))
                    KCheck.stringLenInInterval(
                        nano_configuration_2_qry.semi_offline_on_uart_receive_batch,
                        GlobalConsts.get('const_semi_offline_batch_lenmin'),
                        GlobalConsts.get('const_semi_offline_batch_size')
                    )
            if dict_params.get('scankey_encoding') is not None:
                param_failed = 'scankey_encoding'
                nano_configuration_2_qry.scankey_encoding = KCheck.elementInList(dict_params.get('scankey_encoding'), GlobalConsts.get('const_scankey_encoding_values'))
            if dict_params.get('kybmgr_enabled') is not None:
                param_failed = 'kybmgr_enabled'
                nano_configuration_2_qry.kybmgr_enabled = KCheck.booleanValue(dict_params.get('kybmgr_enabled'))
            if dict_params.get('kybmgr_cfg_1') is not None:
                param_failed = 'kybmgr_cfg_1'
                if dict_params.get('kybmgr_cfg_1') == '':
                    nano_configuration_2_qry.kybmgr_cfg_1 = ''
                else:
                    nano_configuration_2_qry.kybmgr_cfg_1 = json.dumps(json.loads(dict_params.get('kybmgr_cfg_1')))
                    KCheck.stringLenInInterval(
                        nano_configuration_2_qry.kybmgr_cfg_1,
                        GlobalConsts.get('const_kybmgr_cfg_1_lenmin'),
                        GlobalConsts.get('const_kybmgr_cfg_1_size')
                    )
            if dict_params.get('screen_html_boot') is not None:
                param_failed = 'screen_html_boot'
                nano_configuration_2_qry.screen_html_boot = KCheck.stringLenInInterval(
                    dict_params.get('screen_html_boot'),
                    GlobalConsts.get('const_screen_html_boot_lenmin'),
                    GlobalConsts.get('const_screen_html_boot_size'))
            db.session.add(nano_configuration_2_qry)
            db.session.commit()
            db.session.close()
            return KtpRet.RET_OK, None
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.rollback()
            db.session.close()
            return KtpRet.RET_INVALIDARGUMENT, param_failed

    def apply(self):
        try:
            b_hem_de_rebotar_rtc = False
            b_hem_de_rebotar_network = False
            b_hem_de_rebotar_wlan = False
            b_hem_de_rebotar_interface = False
            b_hem_de_rebotar_ktp = False
            b_hem_de_rebotar_jso = False
            b_hem_de_rebotar_http = False
            b_hem_de_rebotar_cloud = False
            b_hem_de_rebotar_semi_offline = False
            b_hem_de_rebotar_scankey = False
            b_hem_de_rebotar_kybmgr = False
            nano_configuration_1_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 1).first()
            nano_configuration_2_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 2).first()
            if nano_configuration_1_qry is None or nano_configuration_2_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION, False

            # RTC
            if nano_configuration_1_qry.rtc_local_timezone != nano_configuration_2_qry.rtc_local_timezone:
                # Ens han canviat el Timezone. Haurem de rebotar
                b_hem_de_rebotar_rtc = True
            nano_configuration_1_qry.rtc_local_timezone = nano_configuration_2_qry.rtc_local_timezone

            # Network Nanopi
            if nano_configuration_1_qry.network_dhcp_mode != nano_configuration_2_qry.network_dhcp_mode:
                # Ens han canviat de DHCP a Manual o Viceversa
                b_hem_de_rebotar_network = True
            else:
                if nano_configuration_2_qry.network_dhcp_mode == "Manual":
                    if nano_configuration_2_qry.network_ip_address is not None:
                        if nano_configuration_1_qry.network_ip_address != nano_configuration_2_qry.network_ip_address:
                            # Ens han canviat la IP del Nanopi
                            b_hem_de_rebotar_network = True
                    if nano_configuration_2_qry.network_bits_mask is not None:
                        if nano_configuration_1_qry.network_bits_mask != nano_configuration_2_qry.network_bits_mask:
                            # Ens han canviat la màscara
                            b_hem_de_rebotar_network = True
                    if nano_configuration_2_qry.network_ip_router is not None:
                        if nano_configuration_1_qry.network_ip_router != nano_configuration_2_qry.network_ip_router:
                            # Ens han canviat la ip del router
                            b_hem_de_rebotar_network = True
            nano_configuration_1_qry.network_dhcp_mode = nano_configuration_2_qry.network_dhcp_mode
            nano_configuration_1_qry.network_ip_address = nano_configuration_2_qry.network_ip_address
            nano_configuration_1_qry.network_bits_mask = nano_configuration_2_qry.network_bits_mask
            nano_configuration_1_qry.network_ip_router = nano_configuration_2_qry.network_ip_router

            # WLAN Nanopi
            initial_wlan_enabled = nano_configuration_1_qry.wlan_enabled
            initial_wlan_ssid = nano_configuration_1_qry.wlan_ssid
            initial_wlan_password = nano_configuration_1_qry.wlan_password
            if nano_configuration_1_qry.wlan_enabled != nano_configuration_2_qry.wlan_enabled:
                # Ens han activat o desactivat la wifi
                b_hem_de_rebotar_wlan = True
            else:
                if nano_configuration_2_qry.wlan_enabled:
                    if nano_configuration_2_qry.wlan_ssid is not None:
                        if nano_configuration_1_qry.wlan_ssid != nano_configuration_2_qry.wlan_ssid:
                            # Ens han canviat la SSID del wifi
                            b_hem_de_rebotar_wlan = True
                    if nano_configuration_2_qry.wlan_password is not None:
                        if nano_configuration_1_qry.wlan_password != nano_configuration_2_qry.wlan_password:
                            # Ens han canviat la password del wifi
                            b_hem_de_rebotar_wlan = True
            nano_configuration_1_qry.wlan_enabled = nano_configuration_2_qry.wlan_enabled
            nano_configuration_1_qry.wlan_ssid = nano_configuration_2_qry.wlan_ssid
            nano_configuration_1_qry.wlan_password = nano_configuration_2_qry.wlan_password

            # INTERFACE
            if nano_configuration_1_qry.interface_ins_pwd != nano_configuration_2_qry.interface_ins_pwd:
                # Ens han canviat la password de la interface
                b_hem_de_rebotar_interface = True
            nano_configuration_1_qry.interface_ins_pwd = nano_configuration_2_qry.interface_ins_pwd

            # KTP
            if nano_configuration_1_qry.ktp_interface != nano_configuration_2_qry.ktp_interface:
                # Ens han canviat si hem de fer servir o no la KTP
                b_hem_de_rebotar_ktp = True
            else:
                if nano_configuration_2_qry.ktp_interface:
                    if nano_configuration_2_qry.terminal_description is not None:
                        if nano_configuration_1_qry.terminal_description != nano_configuration_2_qry.terminal_description:
                            # Ens han canviat el terminal_description que fem servir com ktp_terminal_name
                            b_hem_de_rebotar_ktp = True
                    if nano_configuration_2_qry.ktp_server_client_mode is not None:
                        if nano_configuration_1_qry.ktp_server_client_mode != nano_configuration_2_qry.ktp_server_client_mode:
                            # Ens han canviat el ktp_server_client_mode
                            b_hem_de_rebotar_ktp = True
                    if nano_configuration_2_qry.ktp_server_client_mode == "Client":
                        if nano_configuration_2_qry.ktp_remote_server_ip_1 is not None:
                            if nano_configuration_1_qry.ktp_remote_server_ip_1 != nano_configuration_2_qry.ktp_remote_server_ip_1:
                                # Ens han canviat el ktp_remote_server_ip_1
                                b_hem_de_rebotar_ktp = True
                        if nano_configuration_2_qry.ktp_remote_server_ip_2 is not None:
                            if nano_configuration_1_qry.ktp_remote_server_ip_2 != nano_configuration_2_qry.ktp_remote_server_ip_2:
                                # Ens han canviat el ktp_remote_server_ip_2
                                b_hem_de_rebotar_ktp = True
                        if nano_configuration_2_qry.ktp_remote_server_port_1 is not None:
                            if nano_configuration_1_qry.ktp_remote_server_port_1 != nano_configuration_2_qry.ktp_remote_server_port_1:
                                # Ens han canviat el ktp_remote_server_port_1
                                b_hem_de_rebotar_ktp = True
                        if nano_configuration_2_qry.ktp_remote_server_port_2 is not None:
                            if nano_configuration_1_qry.ktp_remote_server_port_2 != nano_configuration_2_qry.ktp_remote_server_port_2:
                                # Ens han canviat el ktp_remote_server_port_2
                                b_hem_de_rebotar_ktp = True
                    if nano_configuration_2_qry.ktp_udp_detect is not None:
                        if nano_configuration_1_qry.ktp_udp_detect != nano_configuration_2_qry.ktp_udp_detect:
                            # Ens han canviat el ktp_udp_detect
                            b_hem_de_rebotar_ktp = True
                    if nano_configuration_2_qry.ktp_udp_detect:
                        if nano_configuration_2_qry.ktp_udp_port is not None:
                            if nano_configuration_1_qry.ktp_udp_port != nano_configuration_2_qry.ktp_udp_port:
                                # Ens han canviat el ktp_udp_port
                                b_hem_de_rebotar_ktp = True
                    if nano_configuration_2_qry.ktp_network_id is not None:
                        if nano_configuration_1_qry.ktp_network_id != nano_configuration_2_qry.ktp_network_id:
                            # Ens han canviat el ktp_network_id
                            b_hem_de_rebotar_ktp = True
                    if nano_configuration_2_qry.ktp_aes256 is not None:
                        if nano_configuration_1_qry.ktp_aes256 != nano_configuration_2_qry.ktp_aes256:
                            # Ens han canviat el ktp_aes256
                            b_hem_de_rebotar_ktp = True

            nano_configuration_1_qry.ktp_interface = nano_configuration_2_qry.ktp_interface
            nano_configuration_1_qry.ktp_server_client_mode = nano_configuration_2_qry.ktp_server_client_mode
            nano_configuration_1_qry.ktp_remote_server_ip_1 = nano_configuration_2_qry.ktp_remote_server_ip_1
            nano_configuration_1_qry.ktp_remote_server_ip_2 = nano_configuration_2_qry.ktp_remote_server_ip_2
            nano_configuration_1_qry.ktp_remote_server_port_1 = nano_configuration_2_qry.ktp_remote_server_port_1
            nano_configuration_1_qry.ktp_remote_server_port_2 = nano_configuration_2_qry.ktp_remote_server_port_2
            nano_configuration_1_qry.ktp_udp_detect = nano_configuration_2_qry.ktp_udp_detect
            nano_configuration_1_qry.ktp_udp_port = nano_configuration_2_qry.ktp_udp_port
            nano_configuration_1_qry.ktp_network_id = nano_configuration_2_qry.ktp_network_id
            nano_configuration_1_qry.ktp_aes256 = nano_configuration_2_qry.ktp_aes256

            # JSO
            if nano_configuration_1_qry.jso_interface != nano_configuration_2_qry.jso_interface:
                # Ens han canviat si hem de fer servir o no interface JSO
                b_hem_de_rebotar_jso = True
            else:
                if nano_configuration_2_qry.jso_interface:
                    if nano_configuration_2_qry.jso_server_client_mode is not None:
                        if nano_configuration_1_qry.jso_server_client_mode != nano_configuration_2_qry.jso_server_client_mode:
                            # Ens han canviat el jso_server_client_mode
                            b_hem_de_rebotar_jso = True
                    if nano_configuration_2_qry.jso_server_client_mode == "Client":
                        if nano_configuration_2_qry.jso_remote_server_ip_1 is not None:
                            if nano_configuration_1_qry.jso_remote_server_ip_1 != nano_configuration_2_qry.jso_remote_server_ip_1:
                                # Ens han canviat el jso_remote_server_ip_1
                                b_hem_de_rebotar_jso = True
                        if nano_configuration_2_qry.jso_remote_server_port_1 is not None:
                            if nano_configuration_1_qry.jso_remote_server_port_1 != nano_configuration_2_qry.jso_remote_server_port_1:
                                # Ens han canviat el jso_remote_server_port_1
                                b_hem_de_rebotar_jso = True
                        if nano_configuration_2_qry.jso_remote_server_ip_2 is not None:
                            if nano_configuration_1_qry.jso_remote_server_ip_2 != nano_configuration_2_qry.jso_remote_server_ip_2:
                                # Ens han canviat el jso_remote_server_ip_2
                                b_hem_de_rebotar_jso = True
                        if nano_configuration_2_qry.jso_remote_server_port_2 is not None:
                            if nano_configuration_1_qry.jso_remote_server_port_2 != nano_configuration_2_qry.jso_remote_server_port_2:
                                # Ens han canviat el jso_remote_server_port_2
                                b_hem_de_rebotar_jso = True
            nano_configuration_1_qry.jso_interface = nano_configuration_2_qry.jso_interface
            nano_configuration_1_qry.jso_server_client_mode = nano_configuration_2_qry.jso_server_client_mode
            nano_configuration_1_qry.jso_remote_server_ip_1 = nano_configuration_2_qry.jso_remote_server_ip_1
            nano_configuration_1_qry.jso_remote_server_port_1 = nano_configuration_2_qry.jso_remote_server_port_1
            nano_configuration_1_qry.jso_remote_server_ip_2 = nano_configuration_2_qry.jso_remote_server_ip_2
            nano_configuration_1_qry.jso_remote_server_port_2 = nano_configuration_2_qry.jso_remote_server_port_2

            # HTTP
            if nano_configuration_1_qry.http_interface != nano_configuration_2_qry.http_interface:
                # Ens han canviat si hem de fer servir o no interface HTTP SOCKETIO
                b_hem_de_rebotar_http = True
            else:
                if nano_configuration_2_qry.http_interface:
                    if nano_configuration_2_qry.http_socketio_server_host is not None:
                        if nano_configuration_1_qry.http_socketio_server_host != nano_configuration_2_qry.http_socketio_server_host:
                            # Ens han canviat el http_socketio_server_host
                            b_hem_de_rebotar_http = True
                    if nano_configuration_2_qry.http_socketio_server_port is not None:
                        if nano_configuration_1_qry.http_socketio_server_port != nano_configuration_2_qry.http_socketio_server_port:
                            # Ens han canviat el http_socketio_server_port
                            b_hem_de_rebotar_http = True
            nano_configuration_1_qry.http_interface = nano_configuration_2_qry.http_interface
            nano_configuration_1_qry.http_socketio_server_host = nano_configuration_2_qry.http_socketio_server_host
            nano_configuration_1_qry.http_socketio_server_port = nano_configuration_2_qry.http_socketio_server_port

            # CLOUD
            if nano_configuration_1_qry.cloud_interface != nano_configuration_2_qry.cloud_interface:
                # Ens han canviat si hem de fer servir o no interface CLOUD
                b_hem_de_rebotar_cloud = True
            else:
                if nano_configuration_2_qry.cloud_interface:
                    if nano_configuration_2_qry.cloud_remote_server_url is not None:
                        if nano_configuration_1_qry.cloud_remote_server_url != nano_configuration_2_qry.cloud_remote_server_url:
                            # Ens han canviat el cloud_remote_server_url
                            b_hem_de_rebotar_cloud = True
                    if nano_configuration_2_qry.cloud_remote_server_token is not None:
                        if nano_configuration_1_qry.cloud_remote_server_token != nano_configuration_2_qry.cloud_remote_server_token:
                            # Ens han canviat el cloud_remote_server_token
                            b_hem_de_rebotar_cloud = True
                    if nano_configuration_2_qry.cloud_allowed_events is not None:
                        if nano_configuration_1_qry.cloud_allowed_events != nano_configuration_2_qry.cloud_allowed_events:
                            # Ens han canviat el cloud_allowed_events
                            b_hem_de_rebotar_cloud = True
                    if nano_configuration_2_qry.cloud_keep_alive_timeout is not None:
                        if nano_configuration_1_qry.cloud_keep_alive_timeout != nano_configuration_2_qry.cloud_keep_alive_timeout:
                            # Ens han canviat el cloud_keep_alive_timeout
                            b_hem_de_rebotar_cloud = True
                    if nano_configuration_2_qry.cloud_busy_relay is not None:
                        if nano_configuration_1_qry.cloud_busy_relay != nano_configuration_2_qry.cloud_busy_relay:
                            # Ens han canviat el cloud_busy_relay
                            b_hem_de_rebotar_cloud = True

            nano_configuration_1_qry.cloud_interface = nano_configuration_2_qry.cloud_interface
            nano_configuration_1_qry.cloud_remote_server_url = nano_configuration_2_qry.cloud_remote_server_url
            nano_configuration_1_qry.cloud_remote_server_token = nano_configuration_2_qry.cloud_remote_server_token
            nano_configuration_1_qry.cloud_allowed_events = nano_configuration_2_qry.cloud_allowed_events
            nano_configuration_1_qry.cloud_keep_alive_timeout = nano_configuration_2_qry.cloud_keep_alive_timeout
            nano_configuration_1_qry.cloud_busy_relay = nano_configuration_2_qry.cloud_busy_relay

            # BATCH D' INSTRUCCIONS EN MODE SEMI OFFLINE
            if nano_configuration_1_qry.semi_offline_mode_enabled != nano_configuration_2_qry.semi_offline_mode_enabled:
                # Ens han canviat si hem de fer servir o no Semi Offline
                b_hem_de_rebotar_semi_offline = True
            else:
                if nano_configuration_2_qry.semi_offline_mode_enabled:
                    if nano_configuration_1_qry.semi_offline_keep_alive_timeout != nano_configuration_2_qry.semi_offline_keep_alive_timeout:
                        b_hem_de_rebotar_semi_offline = True
                    if nano_configuration_1_qry.semi_offline_on_semi_offline_mode_enter_batch != nano_configuration_2_qry.semi_offline_on_semi_offline_mode_enter_batch:
                        b_hem_de_rebotar_semi_offline = True
                    if nano_configuration_1_qry.semi_offline_on_usrtimer_elapsed_batch != nano_configuration_2_qry.semi_offline_on_usrtimer_elapsed_batch:
                        b_hem_de_rebotar_semi_offline = True
                    if nano_configuration_1_qry.semi_offline_on_mifare_track_batch != nano_configuration_2_qry.semi_offline_on_mifare_track_batch:
                        b_hem_de_rebotar_semi_offline = True
                    if nano_configuration_1_qry.semi_offline_on_ttl_track_batch != nano_configuration_2_qry.semi_offline_on_ttl_track_batch:
                        b_hem_de_rebotar_semi_offline = True
                    if nano_configuration_1_qry.semi_offline_on_fim_finger_batch != nano_configuration_2_qry.semi_offline_on_fim_finger_batch:
                        b_hem_de_rebotar_semi_offline = True
                    if nano_configuration_1_qry.semi_offline_on_sfm_finger_batch != nano_configuration_2_qry.semi_offline_on_sfm_finger_batch:
                        b_hem_de_rebotar_semi_offline = True
                    if nano_configuration_1_qry.semi_offline_on_keyboard_echo_batch != nano_configuration_2_qry.semi_offline_on_keyboard_echo_batch:
                        b_hem_de_rebotar_semi_offline = True
                    if nano_configuration_1_qry.semi_offline_on_uart_receive_batch != nano_configuration_2_qry.semi_offline_on_uart_receive_batch:
                        b_hem_de_rebotar_semi_offline = True

            nano_configuration_1_qry.semi_offline_mode_enabled = nano_configuration_2_qry.semi_offline_mode_enabled
            nano_configuration_1_qry.semi_offline_keep_alive_timeout = nano_configuration_2_qry.semi_offline_keep_alive_timeout
            nano_configuration_1_qry.semi_offline_on_semi_offline_mode_enter_batch = nano_configuration_2_qry.semi_offline_on_semi_offline_mode_enter_batch
            nano_configuration_1_qry.semi_offline_on_usrtimer_elapsed_batch = nano_configuration_2_qry.semi_offline_on_usrtimer_elapsed_batch
            nano_configuration_1_qry.semi_offline_on_mifare_track_batch = nano_configuration_2_qry.semi_offline_on_mifare_track_batch
            nano_configuration_1_qry.semi_offline_on_ttl_track_batch = nano_configuration_2_qry.semi_offline_on_ttl_track_batch
            nano_configuration_1_qry.semi_offline_on_fim_finger_batch = nano_configuration_2_qry.semi_offline_on_fim_finger_batch
            nano_configuration_1_qry.semi_offline_on_sfm_finger_batch = nano_configuration_2_qry.semi_offline_on_sfm_finger_batch
            nano_configuration_1_qry.semi_offline_on_keyboard_echo_batch = nano_configuration_2_qry.semi_offline_on_keyboard_echo_batch
            nano_configuration_1_qry.semi_offline_on_uart_receive_batch = nano_configuration_2_qry.semi_offline_on_uart_receive_batch

            # MODUL SCANKEY
            if nano_configuration_1_qry.scankey_encoding != nano_configuration_2_qry.scankey_encoding:
                # Ens han canviat el model de teclat
                b_hem_de_rebotar_scankey = True

            nano_configuration_1_qry.scankey_encoding = nano_configuration_2_qry.scankey_encoding

            # MODUL KYB-MGR
            if nano_configuration_1_qry.kybmgr_enabled != nano_configuration_2_qry.kybmgr_enabled:
                # Ens han canviat si hem de fer servir o no MgrKybmgr
                b_hem_de_rebotar_kybmgr = True
            else:
                if nano_configuration_2_qry.kybmgr_enabled:
                    if nano_configuration_1_qry.kybmgr_cfg_1 != nano_configuration_2_qry.kybmgr_cfg_1:
                        b_hem_de_rebotar_kybmgr = True

            nano_configuration_1_qry.kybmgr_enabled = nano_configuration_2_qry.kybmgr_enabled
            nano_configuration_1_qry.kybmgr_cfg_1 = nano_configuration_2_qry.kybmgr_cfg_1

            # MODUL SCREEN (no té gestió de b_hem_de_rebotar_screen)
            nano_configuration_1_qry.screen_html_boot = nano_configuration_2_qry.screen_html_boot

            # terminal (el gravem al final perquè pot afectar l'anàlisi de reboot de diversos protocols)
            nano_configuration_1_qry.terminal_description = nano_configuration_2_qry.terminal_description

            #rebotar
            if b_hem_de_rebotar_wlan:
                w_w_i_p = self.mgr_kapriassist.WriteWifiInterfaceParameters(nano_configuration_2_qry.wlan_enabled, nano_configuration_2_qry.wlan_ssid, nano_configuration_2_qry.wlan_password)
                if w_w_i_p != 'OK':
                    # restaurem a nmcli els paràmetres anteriorment aplicats
                    self.mgr_kapriassist.WriteWifiInterfaceParameters(initial_wlan_enabled, initial_wlan_ssid, initial_wlan_password)
                    db.session.close()
                    return KtpRet.RET_FAILED, False
            if b_hem_de_rebotar_rtc:
                s_t = self.mgr_kapriassist.set_timezone(nano_configuration_2_qry.rtc_local_timezone)
                if s_t != 'OK':
                    db.session.close()
                    return KtpRet.RET_FAILED, False
            if b_hem_de_rebotar_network:
                w_e_i_p = self.mgr_kapriassist.WriteEthernetInterfaceParameters(nano_configuration_2_qry.network_dhcp_mode, nano_configuration_2_qry.network_ip_address, nano_configuration_2_qry.network_bits_mask, nano_configuration_2_qry.network_ip_router)
                if w_e_i_p != 'OK':
                    db.session.close()
                    return KtpRet.RET_FAILED, False

            db.session.commit()
            db.session.close()

            if b_hem_de_rebotar_interface:
                self.mgr_interface_global.start()
            if b_hem_de_rebotar_ktp:
                self.mgr_ktpterminal.start()
            if b_hem_de_rebotar_jso:
                self.mgr_jsoterminal.start()
            if b_hem_de_rebotar_http:
                self.mgr_httpterminal.start()
            if b_hem_de_rebotar_cloud:
                self.mgr_cloudterminal.start()
            if b_hem_de_rebotar_semi_offline:
                self.mgr_semi_offline.start()
            if b_hem_de_rebotar_scankey:
                self.mgr_scankey.start()
            if b_hem_de_rebotar_kybmgr:
                self.mgr_kybmgr_configurer.start()
            return KtpRet.RET_OK, b_hem_de_rebotar_network
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.rollback()
            db.session.close()
            return KtpRet.RET_EXCEPTION, False

    def read_future(self):
        dict_config = None
        b_config_modified = False
        dict_apply_diffs = {}
        try:
            # Llegim la ultima configuració gravada
            nano_configuration_2_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 2).one()
            dict_config = Utils.get_qry_dict(nano_configuration_2_qry)
            if 'id' in dict_config.keys():
                del dict_config['id']
            # Llegim configuració activa del sistema, per saber si és diferent de la nova que ens han gravat
            # Comparem configuracions gravada a BBDD i la activa (sense id )
            nano_configuration_1_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 1).one()
            aux_dict_activa = Utils.get_qry_dict(nano_configuration_1_qry)
            if 'id' in aux_dict_activa.keys():
                del aux_dict_activa['id']
            if dict_config != aux_dict_activa:
                b_config_modified = True
                # documentem diferències
                for k, v in aux_dict_activa.items():
                    v_to_apply = dict_config[k]
                    if v != v_to_apply:
                        dict_apply_diffs[k] = [v, v_to_apply]
        except Exception as e:
            dict_config = None
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            db.session.close()
            return b_config_modified, dict_config, dict_apply_diffs

    def backup_future(self):
        try:
            nano_configuration_2_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 2).first()
            nano_configuration_3_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 3).first()
            if nano_configuration_2_qry is None or nano_configuration_3_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION

            nano_configuration_3_qry.terminal_description = nano_configuration_2_qry.terminal_description
            nano_configuration_3_qry.rtc_local_timezone = nano_configuration_2_qry.rtc_local_timezone
            nano_configuration_3_qry.network_ip_address = nano_configuration_2_qry.network_ip_address
            nano_configuration_3_qry.network_bits_mask = nano_configuration_2_qry.network_bits_mask
            nano_configuration_3_qry.network_ip_router = nano_configuration_2_qry.network_ip_router
            nano_configuration_3_qry.network_dhcp_mode = nano_configuration_2_qry.network_dhcp_mode
            nano_configuration_3_qry.wlan_enabled = nano_configuration_2_qry.wlan_enabled
            nano_configuration_3_qry.wlan_ssid = nano_configuration_2_qry.wlan_ssid
            nano_configuration_3_qry.wlan_password = nano_configuration_2_qry.wlan_password
            nano_configuration_3_qry.interface_ins_pwd = nano_configuration_2_qry.interface_ins_pwd
            nano_configuration_3_qry.ktp_interface = nano_configuration_2_qry.ktp_interface
            nano_configuration_3_qry.ktp_server_client_mode = nano_configuration_2_qry.ktp_server_client_mode
            nano_configuration_3_qry.ktp_remote_server_ip_1 = nano_configuration_2_qry.ktp_remote_server_ip_1
            nano_configuration_3_qry.ktp_remote_server_ip_2 = nano_configuration_2_qry.ktp_remote_server_ip_2
            nano_configuration_3_qry.ktp_remote_server_port_1 = nano_configuration_2_qry.ktp_remote_server_port_1
            nano_configuration_3_qry.ktp_remote_server_port_2 = nano_configuration_2_qry.ktp_remote_server_port_2
            nano_configuration_3_qry.ktp_udp_detect = nano_configuration_2_qry.ktp_udp_detect
            nano_configuration_3_qry.ktp_udp_port = nano_configuration_2_qry.ktp_udp_port
            nano_configuration_3_qry.ktp_network_id = nano_configuration_2_qry.ktp_network_id
            nano_configuration_3_qry.ktp_aes256 = nano_configuration_2_qry.ktp_aes256
            nano_configuration_3_qry.jso_interface = nano_configuration_2_qry.jso_interface
            nano_configuration_3_qry.jso_server_client_mode = nano_configuration_2_qry.jso_server_client_mode
            nano_configuration_3_qry.jso_remote_server_ip_1 = nano_configuration_2_qry.jso_remote_server_ip_1
            nano_configuration_3_qry.jso_remote_server_port_1 = nano_configuration_2_qry.jso_remote_server_port_1
            nano_configuration_3_qry.jso_remote_server_ip_2 = nano_configuration_2_qry.jso_remote_server_ip_2
            nano_configuration_3_qry.jso_remote_server_port_2 = nano_configuration_2_qry.jso_remote_server_port_2
            nano_configuration_3_qry.http_interface = nano_configuration_2_qry.http_interface
            nano_configuration_3_qry.http_socketio_server_host = nano_configuration_2_qry.http_socketio_server_host
            nano_configuration_3_qry.http_socketio_server_port = nano_configuration_2_qry.http_socketio_server_port
            nano_configuration_3_qry.cloud_interface = nano_configuration_2_qry.cloud_interface
            nano_configuration_3_qry.cloud_remote_server_url = nano_configuration_2_qry.cloud_remote_server_url
            nano_configuration_3_qry.cloud_remote_server_token = nano_configuration_2_qry.cloud_remote_server_token
            nano_configuration_3_qry.cloud_allowed_events = nano_configuration_2_qry.cloud_allowed_events
            nano_configuration_3_qry.cloud_keep_alive_timeout = nano_configuration_2_qry.cloud_keep_alive_timeout
            nano_configuration_3_qry.cloud_busy_relay = nano_configuration_2_qry.cloud_busy_relay
            nano_configuration_3_qry.semi_offline_mode_enabled = nano_configuration_2_qry.semi_offline_mode_enabled
            nano_configuration_3_qry.semi_offline_keep_alive_timeout = nano_configuration_2_qry.semi_offline_keep_alive_timeout
            nano_configuration_3_qry.semi_offline_on_semi_offline_mode_enter_batch = nano_configuration_2_qry.semi_offline_on_semi_offline_mode_enter_batch
            nano_configuration_3_qry.semi_offline_on_usrtimer_elapsed_batch = nano_configuration_2_qry.semi_offline_on_usrtimer_elapsed_batch
            nano_configuration_3_qry.semi_offline_on_mifare_track_batch = nano_configuration_2_qry.semi_offline_on_mifare_track_batch
            nano_configuration_3_qry.semi_offline_on_ttl_track_batch = nano_configuration_2_qry.semi_offline_on_ttl_track_batch
            nano_configuration_3_qry.semi_offline_on_fim_finger_batch = nano_configuration_2_qry.semi_offline_on_fim_finger_batch
            nano_configuration_3_qry.semi_offline_on_sfm_finger_batch = nano_configuration_2_qry.semi_offline_on_sfm_finger_batch
            nano_configuration_3_qry.semi_offline_on_keyboard_echo_batch = nano_configuration_2_qry.semi_offline_on_keyboard_echo_batch
            nano_configuration_3_qry.semi_offline_on_uart_receive_batch = nano_configuration_2_qry.semi_offline_on_uart_receive_batch
            nano_configuration_3_qry.scankey_encoding = nano_configuration_2_qry.scankey_encoding
            nano_configuration_3_qry.kybmgr_enabled = nano_configuration_2_qry.kybmgr_enabled
            nano_configuration_3_qry.kybmgr_cfg_1 = nano_configuration_2_qry.kybmgr_cfg_1
            nano_configuration_3_qry.screen_html_boot = nano_configuration_2_qry.screen_html_boot

            db.session.commit()
            db.session.close()
            return KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.rollback()
            db.session.close()
            return KtpRet.RET_EXCEPTION

    def restore_future(self):
        try:
            nano_configuration_2_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 2).first()
            nano_configuration_3_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 3).first()
            if nano_configuration_2_qry is None or nano_configuration_3_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION

            nano_configuration_2_qry.terminal_description = nano_configuration_3_qry.terminal_description
            nano_configuration_2_qry.rtc_local_timezone = nano_configuration_3_qry.rtc_local_timezone
            nano_configuration_2_qry.network_ip_address = nano_configuration_3_qry.network_ip_address
            nano_configuration_2_qry.network_bits_mask = nano_configuration_3_qry.network_bits_mask
            nano_configuration_2_qry.network_ip_router = nano_configuration_3_qry.network_ip_router
            nano_configuration_2_qry.network_dhcp_mode = nano_configuration_3_qry.network_dhcp_mode
            nano_configuration_2_qry.wlan_enabled = nano_configuration_3_qry.wlan_enabled
            nano_configuration_2_qry.wlan_ssid = nano_configuration_3_qry.wlan_ssid
            nano_configuration_2_qry.wlan_password = nano_configuration_3_qry.wlan_password
            nano_configuration_2_qry.interface_ins_pwd = nano_configuration_3_qry.interface_ins_pwd
            nano_configuration_2_qry.ktp_interface = nano_configuration_3_qry.ktp_interface
            nano_configuration_2_qry.ktp_server_client_mode = nano_configuration_3_qry.ktp_server_client_mode
            nano_configuration_2_qry.ktp_remote_server_ip_1 = nano_configuration_3_qry.ktp_remote_server_ip_1
            nano_configuration_2_qry.ktp_remote_server_ip_2 = nano_configuration_3_qry.ktp_remote_server_ip_2
            nano_configuration_2_qry.ktp_remote_server_port_1 = nano_configuration_3_qry.ktp_remote_server_port_1
            nano_configuration_2_qry.ktp_remote_server_port_2 = nano_configuration_3_qry.ktp_remote_server_port_2
            nano_configuration_2_qry.ktp_udp_detect = nano_configuration_3_qry.ktp_udp_detect
            nano_configuration_2_qry.ktp_udp_port = nano_configuration_3_qry.ktp_udp_port
            nano_configuration_2_qry.ktp_network_id = nano_configuration_3_qry.ktp_network_id
            nano_configuration_2_qry.ktp_aes256 = nano_configuration_3_qry.ktp_aes256
            nano_configuration_2_qry.jso_interface = nano_configuration_3_qry.jso_interface
            nano_configuration_2_qry.jso_server_client_mode = nano_configuration_3_qry.jso_server_client_mode
            nano_configuration_2_qry.jso_remote_server_ip_1 = nano_configuration_3_qry.jso_remote_server_ip_1
            nano_configuration_2_qry.jso_remote_server_port_1 = nano_configuration_3_qry.jso_remote_server_port_1
            nano_configuration_2_qry.jso_remote_server_ip_2 = nano_configuration_3_qry.jso_remote_server_ip_2
            nano_configuration_2_qry.jso_remote_server_port_2 = nano_configuration_3_qry.jso_remote_server_port_2
            nano_configuration_2_qry.http_interface = nano_configuration_3_qry.http_interface
            nano_configuration_2_qry.http_socketio_server_host = nano_configuration_3_qry.http_socketio_server_host
            nano_configuration_2_qry.http_socketio_server_port = nano_configuration_3_qry.http_socketio_server_port
            nano_configuration_2_qry.cloud_interface = nano_configuration_3_qry.cloud_interface
            nano_configuration_2_qry.cloud_remote_server_url = nano_configuration_3_qry.cloud_remote_server_url
            nano_configuration_2_qry.cloud_remote_server_token = nano_configuration_3_qry.cloud_remote_server_token
            nano_configuration_2_qry.cloud_allowed_events = nano_configuration_3_qry.cloud_allowed_events
            nano_configuration_2_qry.cloud_keep_alive_timeout = nano_configuration_3_qry.cloud_keep_alive_timeout
            nano_configuration_2_qry.cloud_busy_relay = nano_configuration_3_qry.cloud_busy_relay
            nano_configuration_2_qry.semi_offline_mode_enabled = nano_configuration_3_qry.semi_offline_mode_enabled
            nano_configuration_2_qry.semi_offline_keep_alive_timeout = nano_configuration_3_qry.semi_offline_keep_alive_timeout
            nano_configuration_2_qry.semi_offline_on_semi_offline_mode_enter_batch = nano_configuration_3_qry.semi_offline_on_semi_offline_mode_enter_batch
            nano_configuration_2_qry.semi_offline_on_usrtimer_elapsed_batch = nano_configuration_3_qry.semi_offline_on_usrtimer_elapsed_batch
            nano_configuration_2_qry.semi_offline_on_mifare_track_batch = nano_configuration_3_qry.semi_offline_on_mifare_track_batch
            nano_configuration_2_qry.semi_offline_on_ttl_track_batch = nano_configuration_3_qry.semi_offline_on_ttl_track_batch
            nano_configuration_2_qry.semi_offline_on_fim_finger_batch = nano_configuration_3_qry.semi_offline_on_fim_finger_batch
            nano_configuration_2_qry.semi_offline_on_sfm_finger_batch = nano_configuration_3_qry.semi_offline_on_sfm_finger_batch
            nano_configuration_2_qry.semi_offline_on_keyboard_echo_batch = nano_configuration_3_qry.semi_offline_on_keyboard_echo_batch
            nano_configuration_2_qry.semi_offline_on_uart_receive_batch = nano_configuration_3_qry.semi_offline_on_uart_receive_batch
            nano_configuration_2_qry.scankey_encoding = nano_configuration_3_qry.scankey_encoding
            nano_configuration_2_qry.kybmgr_enabled = nano_configuration_3_qry.kybmgr_enabled
            nano_configuration_2_qry.kybmgr_cfg_1 = nano_configuration_3_qry.kybmgr_cfg_1
            nano_configuration_2_qry.screen_html_boot = nano_configuration_3_qry.screen_html_boot

            db.session.commit()
            db.session.close()
            return KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.rollback()
            db.session.close()
            return KtpRet.RET_EXCEPTION

    def backup_factory(self):
        try:
            nano_configuration_2_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 2).first()
            nano_configuration_4_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 4).first()
            if nano_configuration_2_qry is None or nano_configuration_4_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION

            nano_configuration_4_qry.terminal_description = nano_configuration_2_qry.terminal_description
            nano_configuration_4_qry.rtc_local_timezone = nano_configuration_2_qry.rtc_local_timezone
            nano_configuration_4_qry.network_ip_address = nano_configuration_2_qry.network_ip_address
            nano_configuration_4_qry.network_bits_mask = nano_configuration_2_qry.network_bits_mask
            nano_configuration_4_qry.network_ip_router = nano_configuration_2_qry.network_ip_router
            nano_configuration_4_qry.network_dhcp_mode = nano_configuration_2_qry.network_dhcp_mode
            nano_configuration_4_qry.wlan_enabled = nano_configuration_2_qry.wlan_enabled
            nano_configuration_4_qry.wlan_ssid = nano_configuration_2_qry.wlan_ssid
            nano_configuration_4_qry.wlan_password = nano_configuration_2_qry.wlan_password
            nano_configuration_4_qry.interface_ins_pwd = nano_configuration_2_qry.interface_ins_pwd
            nano_configuration_4_qry.ktp_interface = nano_configuration_2_qry.ktp_interface
            nano_configuration_4_qry.ktp_server_client_mode = nano_configuration_2_qry.ktp_server_client_mode
            nano_configuration_4_qry.ktp_remote_server_ip_1 = nano_configuration_2_qry.ktp_remote_server_ip_1
            nano_configuration_4_qry.ktp_remote_server_ip_2 = nano_configuration_2_qry.ktp_remote_server_ip_2
            nano_configuration_4_qry.ktp_remote_server_port_1 = nano_configuration_2_qry.ktp_remote_server_port_1
            nano_configuration_4_qry.ktp_remote_server_port_2 = nano_configuration_2_qry.ktp_remote_server_port_2
            nano_configuration_4_qry.ktp_udp_detect = nano_configuration_2_qry.ktp_udp_detect
            nano_configuration_4_qry.ktp_udp_port = nano_configuration_2_qry.ktp_udp_port
            nano_configuration_4_qry.ktp_network_id = nano_configuration_2_qry.ktp_network_id
            nano_configuration_4_qry.ktp_aes256 = nano_configuration_2_qry.ktp_aes256
            nano_configuration_4_qry.jso_interface = nano_configuration_2_qry.jso_interface
            nano_configuration_4_qry.jso_server_client_mode = nano_configuration_2_qry.jso_server_client_mode
            nano_configuration_4_qry.jso_remote_server_ip_1 = nano_configuration_2_qry.jso_remote_server_ip_1
            nano_configuration_4_qry.jso_remote_server_port_1 = nano_configuration_2_qry.jso_remote_server_port_1
            nano_configuration_4_qry.jso_remote_server_ip_2 = nano_configuration_2_qry.jso_remote_server_ip_2
            nano_configuration_4_qry.jso_remote_server_port_2 = nano_configuration_2_qry.jso_remote_server_port_2
            nano_configuration_4_qry.http_interface = nano_configuration_2_qry.http_interface
            nano_configuration_4_qry.http_socketio_server_host = nano_configuration_2_qry.http_socketio_server_host
            nano_configuration_4_qry.http_socketio_server_port = nano_configuration_2_qry.http_socketio_server_port
            nano_configuration_4_qry.cloud_interface = nano_configuration_2_qry.cloud_interface
            nano_configuration_4_qry.cloud_remote_server_url = nano_configuration_2_qry.cloud_remote_server_url
            nano_configuration_4_qry.cloud_remote_server_token = nano_configuration_2_qry.cloud_remote_server_token
            nano_configuration_4_qry.cloud_allowed_events = nano_configuration_2_qry.cloud_allowed_events
            nano_configuration_4_qry.cloud_keep_alive_timeout = nano_configuration_2_qry.cloud_keep_alive_timeout
            nano_configuration_4_qry.cloud_busy_relay = nano_configuration_2_qry.cloud_busy_relay
            nano_configuration_4_qry.semi_offline_mode_enabled = nano_configuration_2_qry.semi_offline_mode_enabled
            nano_configuration_4_qry.semi_offline_keep_alive_timeout = nano_configuration_2_qry.semi_offline_keep_alive_timeout
            nano_configuration_4_qry.semi_offline_on_semi_offline_mode_enter_batch = nano_configuration_2_qry.semi_offline_on_semi_offline_mode_enter_batch
            nano_configuration_4_qry.semi_offline_on_usrtimer_elapsed_batch = nano_configuration_2_qry.semi_offline_on_usrtimer_elapsed_batch
            nano_configuration_4_qry.semi_offline_on_mifare_track_batch = nano_configuration_2_qry.semi_offline_on_mifare_track_batch
            nano_configuration_4_qry.semi_offline_on_ttl_track_batch = nano_configuration_2_qry.semi_offline_on_ttl_track_batch
            nano_configuration_4_qry.semi_offline_on_fim_finger_batch = nano_configuration_2_qry.semi_offline_on_fim_finger_batch
            nano_configuration_4_qry.semi_offline_on_sfm_finger_batch = nano_configuration_2_qry.semi_offline_on_sfm_finger_batch
            nano_configuration_4_qry.semi_offline_on_keyboard_echo_batch = nano_configuration_2_qry.semi_offline_on_keyboard_echo_batch
            nano_configuration_4_qry.semi_offline_on_uart_receive_batch = nano_configuration_2_qry.semi_offline_on_uart_receive_batch
            nano_configuration_4_qry.scankey_encoding = nano_configuration_2_qry.scankey_encoding
            nano_configuration_4_qry.kybmgr_enabled = nano_configuration_2_qry.kybmgr_enabled
            nano_configuration_4_qry.kybmgr_cfg_1 = nano_configuration_2_qry.kybmgr_cfg_1
            nano_configuration_4_qry.screen_html_boot = nano_configuration_2_qry.screen_html_boot

            db.session.commit()
            db.session.close()
            return KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.rollback()
            db.session.close()
            return KtpRet.RET_EXCEPTION

    def restore_factory(self):
        try:
            nano_configuration_2_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 2).first()
            nano_configuration_4_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 4).first()
            if nano_configuration_2_qry is None or nano_configuration_4_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION

            nano_configuration_2_qry.terminal_description = nano_configuration_4_qry.terminal_description
            nano_configuration_2_qry.rtc_local_timezone = nano_configuration_4_qry.rtc_local_timezone
            nano_configuration_2_qry.network_ip_address = nano_configuration_4_qry.network_ip_address
            nano_configuration_2_qry.network_bits_mask = nano_configuration_4_qry.network_bits_mask
            nano_configuration_2_qry.network_ip_router = nano_configuration_4_qry.network_ip_router
            nano_configuration_2_qry.network_dhcp_mode = nano_configuration_4_qry.network_dhcp_mode
            nano_configuration_2_qry.wlan_enabled = nano_configuration_4_qry.wlan_enabled
            nano_configuration_2_qry.wlan_ssid = nano_configuration_4_qry.wlan_ssid
            nano_configuration_2_qry.wlan_password = nano_configuration_4_qry.wlan_password
            nano_configuration_2_qry.interface_ins_pwd = nano_configuration_4_qry.interface_ins_pwd
            nano_configuration_2_qry.ktp_interface = nano_configuration_4_qry.ktp_interface
            nano_configuration_2_qry.ktp_server_client_mode = nano_configuration_4_qry.ktp_server_client_mode
            nano_configuration_2_qry.ktp_remote_server_ip_1 = nano_configuration_4_qry.ktp_remote_server_ip_1
            nano_configuration_2_qry.ktp_remote_server_ip_2 = nano_configuration_4_qry.ktp_remote_server_ip_2
            nano_configuration_2_qry.ktp_remote_server_port_1 = nano_configuration_4_qry.ktp_remote_server_port_1
            nano_configuration_2_qry.ktp_remote_server_port_2 = nano_configuration_4_qry.ktp_remote_server_port_2
            nano_configuration_2_qry.ktp_udp_detect = nano_configuration_4_qry.ktp_udp_detect
            nano_configuration_2_qry.ktp_udp_port = nano_configuration_4_qry.ktp_udp_port
            nano_configuration_2_qry.ktp_network_id = nano_configuration_4_qry.ktp_network_id
            nano_configuration_2_qry.ktp_aes256 = nano_configuration_4_qry.ktp_aes256
            nano_configuration_2_qry.jso_interface = nano_configuration_4_qry.jso_interface
            nano_configuration_2_qry.jso_server_client_mode = nano_configuration_4_qry.jso_server_client_mode
            nano_configuration_2_qry.jso_remote_server_ip_1 = nano_configuration_4_qry.jso_remote_server_ip_1
            nano_configuration_2_qry.jso_remote_server_port_1 = nano_configuration_4_qry.jso_remote_server_port_1
            nano_configuration_2_qry.jso_remote_server_ip_2 = nano_configuration_4_qry.jso_remote_server_ip_2
            nano_configuration_2_qry.jso_remote_server_port_2 = nano_configuration_4_qry.jso_remote_server_port_2
            nano_configuration_2_qry.http_interface = nano_configuration_4_qry.http_interface
            nano_configuration_2_qry.http_socketio_server_host = nano_configuration_4_qry.http_socketio_server_host
            nano_configuration_2_qry.http_socketio_server_port = nano_configuration_4_qry.http_socketio_server_port
            nano_configuration_2_qry.cloud_interface = nano_configuration_4_qry.cloud_interface
            nano_configuration_2_qry.cloud_remote_server_url = nano_configuration_4_qry.cloud_remote_server_url
            nano_configuration_2_qry.cloud_remote_server_token = nano_configuration_4_qry.cloud_remote_server_token
            nano_configuration_2_qry.cloud_allowed_events = nano_configuration_4_qry.cloud_allowed_events
            nano_configuration_2_qry.cloud_keep_alive_timeout = nano_configuration_4_qry.cloud_keep_alive_timeout
            nano_configuration_2_qry.cloud_busy_relay = nano_configuration_4_qry.cloud_busy_relay
            nano_configuration_2_qry.semi_offline_mode_enabled = nano_configuration_4_qry.semi_offline_mode_enabled
            nano_configuration_2_qry.semi_offline_keep_alive_timeout = nano_configuration_4_qry.semi_offline_keep_alive_timeout
            nano_configuration_2_qry.semi_offline_on_semi_offline_mode_enter_batch = nano_configuration_4_qry.semi_offline_on_semi_offline_mode_enter_batch
            nano_configuration_2_qry.semi_offline_on_usrtimer_elapsed_batch = nano_configuration_4_qry.semi_offline_on_usrtimer_elapsed_batch
            nano_configuration_2_qry.semi_offline_on_mifare_track_batch = nano_configuration_4_qry.semi_offline_on_mifare_track_batch
            nano_configuration_2_qry.semi_offline_on_ttl_track_batch = nano_configuration_4_qry.semi_offline_on_ttl_track_batch
            nano_configuration_2_qry.semi_offline_on_fim_finger_batch = nano_configuration_4_qry.semi_offline_on_fim_finger_batch
            nano_configuration_2_qry.semi_offline_on_sfm_finger_batch = nano_configuration_4_qry.semi_offline_on_sfm_finger_batch
            nano_configuration_2_qry.semi_offline_on_keyboard_echo_batch = nano_configuration_4_qry.semi_offline_on_keyboard_echo_batch
            nano_configuration_2_qry.semi_offline_on_uart_receive_batch = nano_configuration_4_qry.semi_offline_on_uart_receive_batch
            nano_configuration_2_qry.scankey_encoding = nano_configuration_4_qry.scankey_encoding
            nano_configuration_2_qry.kybmgr_enabled = nano_configuration_4_qry.kybmgr_enabled
            nano_configuration_2_qry.kybmgr_cfg_1 = nano_configuration_4_qry.kybmgr_cfg_1
            nano_configuration_2_qry.screen_html_boot = nano_configuration_4_qry.screen_html_boot

            db.session.commit()
            db.session.close()
            return KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.rollback()
            db.session.close()
            return KtpRet.RET_EXCEPTION

    @staticmethod
    def check_cloud_allowed_events(s_cloud_allowed_events):
        events_list = [x.strip() for x in s_cloud_allowed_events.split(',') if x != '']
        events_list.sort()
        for event in events_list:
            if event not in ['on_cloud_keep_alive',
                             'on_cpu_boot',
                             'on_semi_offline_mode_leave',
                             'on_usrtimer_elapsed',
                             'on_inout_digital_input_get_echo',
                             'on_mifare_track',
                             'on_ttl_track',
                             'on_fim_finger',
                             'on_sfm_finger',
                             'on_keyboard_echo',
                             'on_uart_receive',
                             'on_optsel_selection']:
                raise Exception('K_Cloud_Allowed_Events_CheckError')
        return ','.join(event for event in events_list)
