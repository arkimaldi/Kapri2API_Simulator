# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import time
import threading
import inspect
import socketio
import logging

from app.post_woman import PostWoman
from app.mgr_images import MgrImages
from app.mgr_hardware_info import MgrHardwareInfo
from app.mgr_kapriassist import MgrKapriassist
from app.mgr_web_users import MgrWebUsers
from app.mgr_interface_global import MgrInterfaceGlobal
from app.mgr_ktpterminal import MgrKtpterminal
from app.mgr_jsoterminal import MgrJsoterminal
from app.mgr_httpterminal import Mgr_Httpterminal
from app.mgr_cloudterminal import MgrCloudterminal
from app.mgr_semi_offline_api_caller import MgrSemiOfflineApiCaller
from app.mgr_semi_offline_events import MgrSemiOfflineEvents
from app.mgr_semi_offline_lists import MgrSemiOfflineLists
from app.mgr_semi_offline import MgrSemiOffline
from app.mgr_knprxupdater import MgrKnprxupdater
from app.mgr_kxphost import MgrKxphost
from app.mgr_device_info import MgrDeviceInfo
from app.mgr_linuxsys import MgrLinuxsys
from app.mgr_discovery import MgrDiscovery
from app.mgr_guispy import MgrGuispy
from app.mgr_lblmgr import MgrLblmgr
from app.mgr_usrtimer import MgrUsrtimer
from app.mgr_scankey import MgrScankey
from app.MgrKybmgr import MgrKybmgr
from app.mgr_kybmgr_configurer import MgrKybmgrConfigurer
from app.MgrOptsel import MgrOptsel
from app.mgr_config_nano import MgrConfigNano
from app.mgr_config_carrier import MgrConfigCarrier
from app.mgr_config_lexamain import MgrConfigLexaMain
from app.mgr_config_lexaaux import MgrConfigLexaAux
from app.mgr_config_kapri import MgrConfigKapri
from app.mgr_carrier_detector import MgrCarrierDetector
from app.mgr_services_detector import MgrServicesDetector
from app.mgr_network import MgrNetwork
from app.mgr_uart_concat import MgrUartConcat
from app.mgr_button import MgrButton
from app.mgr_audit_logs import MgrAuditLogs


class KapriApp:

    def __init__(self, app):
        self.app = app
        #
        self.sio = None
        self.is_sio_first_connection_complete = False
        self.is_interface_global_started = False
        self.is_ktpterminal_started = False
        self.is_jsoterminal_started = False
        self.is_httpterminal_started = False
        self.is_cloudterminal_started = False
        self.is_semi_offline_started = False
        self.mgr_audit_logs = MgrAuditLogs(self.app)
        self.mgr_images = MgrImages(self.app)
        self.mgr_hardware_info = MgrHardwareInfo()
        self.mgr_kapriassist = MgrKapriassist(self.app, self.mgr_hardware_info)
        self.mgr_web_users = MgrWebUsers(self.app, self.mgr_hardware_info, self.mgr_audit_logs)
        self.mgr_interface_global = MgrInterfaceGlobal(self.app)
        self.mgr_knprxupdater = MgrKnprxupdater(self.app)
        self.mgr_device_info = MgrDeviceInfo(self.app, self.mgr_hardware_info, self.mgr_kapriassist, self.mgr_knprxupdater)
        self.mgr_linuxsys = MgrLinuxsys(self.app, self.mgr_hardware_info, self.mgr_kapriassist)
        self.mgr_discovery = MgrDiscovery(self.app, self.mgr_knprxupdater, self.mgr_hardware_info)
        self.mgr_guispy = MgrGuispy(self.app, self.mgr_device_info, self.mgr_linuxsys, self.sio_emit)
        self.mgr_ktpterminal = MgrKtpterminal(self.app, self.mgr_hardware_info)
        self.mgr_jsoterminal = MgrJsoterminal(self.app)
        self.mgr_httpterminal = Mgr_Httpterminal(self.app, self.mgr_hardware_info)
        self.mgr_cloudterminal = MgrCloudterminal(self.app, self.mgr_hardware_info, self.mgr_guispy)
        self.mgr_semi_offline_api_caller = MgrSemiOfflineApiCaller(self.app)
        self.mgr_semi_offline_events = MgrSemiOfflineEvents(self.app)
        self.mgr_semi_offline_lists = MgrSemiOfflineLists(self.app)
        self.mgr_semi_offline = MgrSemiOffline(self.app, self.mgr_semi_offline_api_caller, self.mgr_semi_offline_lists, self.raiser_on_semi_offline_mode_enter, self.raiser_on_semi_offline_mode_leave)

        self.mgr_kxphost = MgrKxphost(self.app, self.mgr_hardware_info)
        self.mgr_lblmgr = MgrLblmgr(self.app)
        self.mgr_usrtimer = MgrUsrtimer(self.app, self.raiser_on_usrtimer_elapsed)
        self.mgr_scankey = MgrScankey(self.app)
        self.mgr_kybmgr = MgrKybmgr(self.app, self.mgr_guispy)
        self.mgr_kybmgr_configurer = MgrKybmgrConfigurer(self.app, self.mgr_kybmgr)
        self.mgr_optsel = MgrOptsel(self.app, self.mgr_guispy, self.buzzer, self.raiser_on_optsel_selection)
        self.mgr_config_nano = MgrConfigNano(
            self.app, self.mgr_kapriassist, self.mgr_interface_global, self.mgr_ktpterminal, self.mgr_jsoterminal,
            self.mgr_httpterminal, self.mgr_cloudterminal, self.mgr_semi_offline, self.mgr_scankey, self.mgr_kybmgr_configurer
        )
        self.mgr_config_carrier = MgrConfigCarrier(self.app, self.mgr_hardware_info, self.mgr_kxphost)
        self.mgr_config_lexamain = MgrConfigLexaMain(self.app, self.mgr_hardware_info, self.mgr_kxphost)
        self.mgr_config_lexaaux = MgrConfigLexaAux(self.app, self.mgr_hardware_info, self.mgr_kxphost)
        self.mgr_config_kapri = MgrConfigKapri(
            self.app, self.mgr_hardware_info, self.mgr_kapriassist, self.mgr_config_nano, self.mgr_config_carrier,
            self.mgr_config_lexamain, self.mgr_config_lexaaux, self.mgr_web_users
        )
        self.mgr_carrier_detector = MgrCarrierDetector(
            self.app, self.mgr_hardware_info, self.mgr_kxphost, self.mgr_config_carrier,
            self.mgr_config_lexamain, self.mgr_config_lexaaux
        )
        self.mgr_services_detector = MgrServicesDetector(
            self.app, self.mgr_kapriassist, self.mgr_ktpterminal, self.mgr_jsoterminal, self.mgr_httpterminal
        )
        self.mgr_network = MgrNetwork(self.app, self.mgr_hardware_info, self.mgr_kapriassist)
        self.mgr_uart_concat_main = MgrUartConcat(self.app, self.raiser_on_uart_receive_main)
        self.mgr_uart_concat_aux = MgrUartConcat(self.app, self.raiser_on_uart_receive_aux)
        self.mgr_button = MgrButton(self.app, self.mgr_config_kapri, self.mgr_audit_logs)

    def start(self):
        self.mgr_network.start()
        self.mgr_carrier_detector.detect()    # és blocant
        self.mgr_discovery.start()
        self.mgr_guispy.start()
        self.mgr_usrtimer.start()
        self.mgr_scankey.start()
        self.mgr_kybmgr.start()
        self.mgr_optsel.start()
        self.mgr_uart_concat_main.start()
        self.mgr_uart_concat_aux.start()
        self.mgr_button.start()
        #
        self.sio = None
        self.is_sio_first_connection_complete = False
        self.sio_listener_thread = threading.Thread(target=self.sio_listener_thread_task, daemon=True)
        self.sio_listener_thread.start()
        while not self.is_sio_first_connection_complete:
            time.sleep(1)
        # espera addicional despres de l'event connect per garantir l'arrencada del kaprijs
        time.sleep(1)
        #
        self.mgr_services_detector.detect() # NO és blocant
        #
        self.is_interface_global_started = False
        self.interface_global_start_thread = threading.Thread(target=self.interface_global_start_thread_task, daemon=True)
        self.interface_global_start_thread.start()
        #
        self.is_ktpterminal_started = False
        self.ktpterminal_start_thread = threading.Thread(target=self.ktpterminal_start_thread_task, daemon=True)
        self.ktpterminal_start_thread.start()
        #
        self.is_jsoterminal_started = False
        self.jsoterminal_start_thread = threading.Thread(target=self.jsoterminal_start_thread_task, daemon=True)
        self.jsoterminal_start_thread.start()
        #
        self.is_httpterminal_started = False
        self.httpterminal_start_thread = threading.Thread(target=self.httpterminal_start_thread_task, daemon=True)
        self.httpterminal_start_thread.start()
        #
        self.is_cloudterminal_started = False
        self.cloudterminal_start_thread = threading.Thread(target=self.cloudterminal_start_thread_task, daemon=True)
        self.cloudterminal_start_thread.start()
        #
        self.is_semi_offline_started = False
        self.semi_offline_start_thread = threading.Thread(target=self.semi_offline_start_thread_task, daemon=True)
        self.semi_offline_start_thread.start()
        while not (
                self.is_interface_global_started and
                self.is_ktpterminal_started and
                self.is_jsoterminal_started and
                self.is_httpterminal_started and
                self.is_cloudterminal_started and
                self.is_semi_offline_started
        ):
            time.sleep(1)
        self.mgr_guispy.signal_message(self.mgr_services_detector.get_message())
        # Configurem el MgrKybmgr després de senyalitzar Ready...
        self.mgr_kybmgr_configurer.start()
        logging.info("######## MgrKybmgr Configured ########")
        # Emetem on_cpu_boot
        self.manage_event_for_all_channels({'msgType': 'on_cpu_boot', 'msgArg': {}})

    def interface_global_start_thread_task(self):
        with self.app.app_context():
            self.mgr_interface_global.start()
            self.is_interface_global_started = True
            logging.info("######## InterfaceGlobal Started #######")

    def ktpterminal_start_thread_task(self):
        with self.app.app_context():
            self.mgr_ktpterminal.start()
            self.is_ktpterminal_started = True
            logging.info("######## KtpTerminal  Started #######")

    def jsoterminal_start_thread_task(self):
        with self.app.app_context():
            self.mgr_jsoterminal.start()
            self.is_jsoterminal_started = True
            logging.info("######## JsoTerminal Started  ########")

    def httpterminal_start_thread_task(self):
        with self.app.app_context():
            self.mgr_httpterminal.start()
            self.is_httpterminal_started = True
            logging.info("######## HttpTerminal Started ########")

    def cloudterminal_start_thread_task(self):
        with self.app.app_context():
            self.mgr_cloudterminal.start()
            self.is_cloudterminal_started = True
            logging.info("######## CloudTerminal Started ########")

    def semi_offline_start_thread_task(self):
        with self.app.app_context():
            self.mgr_semi_offline.start()
            self.is_semi_offline_started = True
            logging.info("######## SemiOffline Started ########")

    def sio_listener_thread_task(self):
        # instanciem el socketio
        b_sortir = False
        while not b_sortir:
            try:
                self.sio = socketio.Client()

                time.sleep(0.5)

                @self.sio.event
                def connect():
                    self.is_sio_first_connection_complete = True
                    logging.info("######## connected to SocketIO Server ########")

                @self.sio.event
                def kproduct_on_in_out_digital_input_get_echo(data):
                    try:
                        sPosition = None
                        sEUI64 = data['sEUI64']
                        # descodifiquem sEUI64
                        if sEUI64 == self.mgr_hardware_info.get('sEUI64'):
                            sPosition = 'main'
                        elif sEUI64 == self.mgr_hardware_info.get('sEUI64_LexaAux'):
                            sPosition = 'aux'
                        elif sEUI64 == self.mgr_hardware_info.get('sEUI64_LexaMain'):
                            sPosition = 'main_expansion'
                        # descodifiquem ucDinValue bit a bit
                        ucDinValue = data['ucDinValue']
                        # composem event
                        if sPosition is not None:
                            del data['sEUI64']
                            del data['ucDinValue']
                            data['sPosition'] = sPosition
                            bDinList = []
                            bDinList.append((ucDinValue & 0x01) != 0)
                            bDinList.append((ucDinValue & 0x02) != 0)
                            if sPosition == 'main':
                                bDinList.append((ucDinValue & 0x04) != 0)
                                bDinList.append((ucDinValue & 0x08) != 0)
                                bDinList.append((ucDinValue & 0x10) != 0)
                            data['bDinValueList'] = bDinList
                            self.manage_event_for_all_channels({'msgType': 'on_inout_digital_input_get_echo', 'msgArg': data})
                            # gestió del botó de reset dels paràmetres de xarxa
                            self.mgr_button.on_sample((ucDinValue & 0x80) != 0)
                    except Exception as e:
                        logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

                @self.sio.event
                def kproduct_on_mifare_track(data):
                    try:
                        sPosition = None
                        sTrackType = None
                        sEUI64 = data['sEUI64']
                        # descodifiquem sEUI64
                        if sEUI64 == self.mgr_hardware_info.get('sEUI64_LexaMain'):
                            sPosition = 'main'
                        elif sEUI64 == self.mgr_hardware_info.get('sEUI64_LexaAux'):
                            sPosition = 'aux'
                        # descodifiquem ucTrackType
                        if data['ucTrackType'] == 1:  # per mif_mode = 'atqa_uid' i 'reversed_atqa_uid'
                            sTrackType = 'atqa_uid'
                        elif data['ucTrackType'] == 2:  # per mif_mode = 'one_block' i 'mad_one_block'
                            sTrackType = 'one_block'
                        elif data['ucTrackType'] == 3:  # per mif_code = 'three_blocks' i 'mad_three_blocks'
                            sTrackType = 'three_blocks'
                        elif data['ucTrackType'] == 4:  # per mif_mode = 'desfire_file'
                            sTrackType = 'desfire_file'
                        elif data['ucTrackType'] == 5:  # per mif_mode = 'multisector'
                            sTrackType = 'multisector'
                        # composem event
                        if sPosition is not None and sTrackType is not None:
                            del data['sEUI64']
                            del data['ucTrackType']
                            data['sPosition'] = sPosition
                            data['sTrackType'] = sTrackType
                            self.manage_event_for_all_channels(self.append_oextra_to_event({'msgType': 'on_mifare_track', 'msgArg': data}))
                    except Exception as e:
                        logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

                @self.sio.event
                def kproduct_on_ttl_track(data):
                    try:
                        sPosition = None
                        sTrackType = None
                        sEUI64 = data['sEUI64']
                        ucSource = data['ucSource']
                        ucTrackType = data['ucTrackType']
                        #descodifiquem ucSource
                        if ucSource == 0:
                            sPosition = 'main'
                        elif ucSource == 1:
                            sPosition = 'aux'
                        # descodifiquem ucTrackType
                        if ucTrackType == 1:
                            sTrackType = 'aba_tk2'
                        elif ucTrackType == 2:
                            sTrackType = 'wiegand_26'
                        elif ucTrackType == 3:
                            sTrackType = 'wiegand_34'
                        elif ucTrackType == 4:
                            sTrackType = 'wiegand_free'
                        # composem event
                        if sEUI64 == self.mgr_hardware_info.get('sEUI64') and sPosition is not None and sTrackType is not None:
                            del data['sEUI64']
                            del data['ucSource']
                            del data['ucTrackType']
                            data['sPosition'] = sPosition
                            data['sTrackType'] = sTrackType
                            self.manage_event_for_all_channels(self.append_oextra_to_event({'msgType': 'on_ttl_track', 'msgArg': data}))
                    except Exception as e:
                        logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

                @self.sio.event
                def kproduct_on_fim_finger(data):
                    try:
                        sPosition = None
                        sEUI64 = data['sEUI64']
                        ucFimNum = data['ucFimNum']
                        # descodifiquem ucFimNum
                        if ucFimNum == 0:
                            sPosition = 'main'
                        elif ucFimNum == 1:
                            sPosition = 'aux'
                        # composem event
                        if sEUI64 == self.mgr_hardware_info.get('sEUI64') and sPosition is not None:
                            del data['sEUI64']
                            del data['ucFimNum']
                            data['sPosition'] = sPosition
                            self.manage_event_for_all_channels(self.append_oextra_to_event({'msgType': 'on_fim_finger', 'msgArg': data}))
                    except Exception as e:
                        logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

                @self.sio.event
                def kproduct_on_sfm_finger(data):
                    try:
                        sPosition = None
                        sEUI64 = data['sEUI64']
                        ucSfmNum = data['ucSfmNum']
                        # descodifiquem ucSfmNum
                        if ucSfmNum == 0:
                            sPosition = 'main'
                        elif ucSfmNum == 1:
                            sPosition = 'aux'
                        # composem event
                        if sEUI64 == self.mgr_hardware_info.get('sEUI64') and sPosition is not None:
                            del data['sEUI64']
                            del data['ucSfmNum']
                            data['sPosition'] = sPosition
                            self.manage_event_for_all_channels(self.append_oextra_to_event({'msgType': 'on_sfm_finger', 'msgArg': data}))
                    except Exception as e:
                        logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

                @self.sio.event
                def kproduct_on_uart_receive(data):
                    try:
                        sPosition = None
                        sEUI64 = data['sEUI64']
                        ucUartNum = data['ucUartNum']
                        # descodifiquem ucUartNum
                        if ucUartNum == 1:
                            sPosition = 'main'
                        elif ucUartNum == 2:
                            sPosition = 'aux'
                        # composem event
                        if sEUI64 == self.mgr_hardware_info.get('sEUI64') and sPosition is not None:
                            del data['sEUI64']
                            del data['ucUartNum']
                            data['sPosition'] = sPosition
                            if sPosition == 'main':
                                self.mgr_uart_concat_main.on_uart_received(data['sData'])
                            elif sPosition == 'aux':
                                self.mgr_uart_concat_aux.on_uart_received(data['sData'])
                            # a través de la seva callback,
                            # UartConcat farà la crida self.ManageKtpJsoHttpEvent({'msgType': 'on_uart_receive', 'msgArg': data})
                            # on data podrà ser el resultat de concatenar les dades de diversos events
                    except Exception as e:
                        logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

                @self.sio.event
                def kproduct_on_keyboard_echo(data):
                    try:
                        sEUI64 = data['sEUI64']
                        if sEUI64 == self.mgr_hardware_info.get('sEUI64'):
                            data['sKey'] = self.mgr_scankey.decode(data.get('sKey'))
                            b_echo_allowed = self.mgr_guispy.on_key_received(data.get('sKey'))
                            if b_echo_allowed:
                                del data['sEUI64']
                                self.mgr_kybmgr.on_key_received(data.get('sKey'))
                                self.mgr_optsel.on_key_received(data.get('sKey'))
                                self.manage_event_for_all_channels(self.append_oextra_to_event({'msgType': 'on_keyboard_echo', 'msgArg': data}, kybmgr=False))
                    except Exception as e:
                        logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

                @self.sio.event
                def disconnect():
                    logging.info("######## disconnected from  SocketIO Server  ########")

                b_sortir = True
            except Exception as e:
                logging.error(f'SocketIO instance - {inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
                time.sleep(1)
        # bucle de connexió/espera
        while True:
            # connectem el socketio
            b_sortir = False
            while not b_sortir:
                try:
                    time.sleep(0.5)
                    socketio_server_host = self.app.config['SOCKETIO']['socketio_server_host']
                    socketio_server_port = self.app.config['SOCKETIO']['socketio_server_port']
                    self.sio.connect(f'http://{socketio_server_host}:{socketio_server_port}')
                    b_sortir = True
                except Exception as e:
                    logging.error(f'SocketIO.connect - {inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
                    time.sleep(1)
            # esperem mentre dura la connexió
            try:
                self.sio.wait()
            except Exception as e:
                logging.error(f'SocketIO.wait - {inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def sio_emit(self, sEventType, sEvent):
        try:
            if self.sio is not None:
                self.sio.emit(sEventType, sEvent)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def append_oextra_to_event(self, event_dict, kybmgr=True, lblmgr=True):
        try:
            # carreguem variables d'oExtra
            kybmgr_dict = self.mgr_kybmgr.get_code_and_description()
            lblmgr_dict = self.mgr_lblmgr.get_data()
            # eliminem la informació que no hem de transmetre
            if not kybmgr:
                kybmgr_dict = None
            if not lblmgr:
                lblmgr_dict = None
            # creem oExtra si cal
            if kybmgr_dict is not None or lblmgr_dict is not None:
                if 'oExtra' not in event_dict['msgArg'].keys():
                    event_dict['msgArg']['oExtra'] = {}
                # afegim els camps d'oExtra...
                # ...kybmgr
                if kybmgr_dict is not None:
                    event_dict['msgArg']['oExtra']['kybmgr'] = kybmgr_dict
                # ...lblmgr
                if lblmgr_dict is not None:
                    event_dict['msgArg']['oExtra']['lblmgr'] = lblmgr_dict
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            return event_dict

    def raiser_on_uart_receive_main(self, s_data):
        data = {'sPosition': 'main', 'sData': s_data}
        self.manage_event_for_all_channels(self.append_oextra_to_event({'msgType': 'on_uart_receive', 'msgArg': data}))

    def raiser_on_uart_receive_aux(self, s_data):
        data = {'sPosition': 'aux', 'sData': s_data}
        self.manage_event_for_all_channels(self.append_oextra_to_event({'msgType': 'on_uart_receive', 'msgArg': data}))

    def raiser_on_usrtimer_elapsed(self):
        self.manage_event_for_all_channels(self.append_oextra_to_event({'msgType': 'on_usrtimer_elapsed', 'msgArg': {}}))

    def raiser_on_semi_offline_mode_enter(self):
        self.manage_event_for_all_channels({'msgType': 'on_semi_offline_mode_enter', 'msgArg': {}})

    def raiser_on_semi_offline_mode_leave(self):
        self.manage_event_for_all_channels({'msgType': 'on_semi_offline_mode_leave', 'msgArg': {}})

    def raiser_on_optsel_selection(self, data):
        self.manage_event_for_all_channels({'msgType': 'on_optsel_selection', 'msgArg': data})

    def manage_event_for_all_channels(self, dictio):
        if self.is_event_discarted_by_optsel(dictio):
            self.buzzer('3-beeps')
        else:
            if self.mgr_semi_offline.is_server_alive():
                self.mgr_ktpterminal.manage_event(dictio)
                self.mgr_jsoterminal.manage_event(dictio)
                self.mgr_httpterminal.manage_event(dictio)
                self.mgr_cloudterminal.manage_event(dictio)
            else:
                self.mgr_semi_offline.manage_event(dictio)

    def is_event_discarted_by_optsel(self, dictio):
        is_gui_event = dictio['msgType'] in [
            'on_mifare_track',
            'on_ttl_track',
            'on_fim_finger',
            'on_uart_receive',
            'on_sfm_finger'
        ]
        is_optsel_running = self.mgr_optsel.is_running()
        return is_optsel_running and is_gui_event

    def buzzer(self, style):
        """
        Crida a Kxp2HostProAPI per gestionar el beeper
        """
        try:
            if style == '1-beep':
                ucMode = 1  # 1-'on'
                ucTime_ds = 1
            else: # '3-beeps'
                ucMode = 2  # 2-'beep_30'
                ucTime_ds = 15

            sEUI64 = self.mgr_hardware_info.get('sEUI64')
            params = f"/api/nodes/{sEUI64}/InOut/BuzzerOperate/0/{ucMode}/{ucTime_ds}"
            my_url = self.app.config['URL']['url_kxphostproapi'] + params
            result = PostWoman.send_get(my_url)
            return result.get('ucInsRet') == 0
        except Exception as e:
            return False
