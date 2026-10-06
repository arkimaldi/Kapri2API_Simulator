# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import time
import queue
import threading
import inspect
import logging

from app.extensions import db
from app.db_models import NanoConfiguration


class MgrGuispy:

    STROKE_TMO = 4          # timeout entre tecles
    LONG_SHOW_TIME = 10     # temps llarg durant el que es mostren els missatges com la IP, EUI...
    SHORT_SHOW_TIME = 3     # temps curt durant el que es mostren els missatges com ready


    def __init__(self, app, mgr_device_info, mgr_linuxsys, sio_emit_FP):
        self.app = app
        self.mgr_device_info = mgr_device_info
        self.mgr_linuxsys = mgr_linuxsys
        self.sio_emit_FP = sio_emit_FP
        #
        self.sequence_mode = 'standard'  # 'standard', 'extended'
        self.estat = 0
        self.last_time = 0
        self.m_oStrokeQueue = queue.Queue()
        self.s_html_last_sent = '<img src="boot.jpg">'
        self.gui_thread = None

    def start(self):
        try:
            nano_configuration_1_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 1).first()
            if nano_configuration_1_qry is not None:
                screen_html_boot = nano_configuration_1_qry.screen_html_boot
                if screen_html_boot not in ['', None]:
                    self.s_html_last_sent = screen_html_boot
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            db.session.close()
        # fils
        self.gui_thread = threading.Thread(target=self.gui_thread_task, daemon=True)
        self.gui_thread.start()

    def signal_message(self, message):
        s_html = f"<h1>{message}... </h1>"
        self.show_html_and_restore(s_html, MgrGuispy.SHORT_SHOW_TIME)

    def write_screen_html(self, s_html):
        if s_html is not None:
            self.s_html_last_sent = s_html
            self.sio_emit_FP('kapri_ins_screen_html_document_write', s_html)

    def on_key_received(self, s_key):
        # tecles B: BACK, C: UP, D: DOWN, A: OK
        if s_key is None:
            return False
        try:
            # control de timeout
            time_stamp = time.time()
            if self.estat in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                if time_stamp - self.last_time >= MgrGuispy.STROKE_TMO:
                    self.estat = 0
            self.last_time = time_stamp
            # control de la seqüència de tecles
            if self.estat in [0, 1, 2, 3, 4]:
                if s_key == 'B':
                    self.estat += 1
            elif self.estat in [5, 6]:
                if s_key == 'C':
                    self.estat += 1
                else:
                    self.estat = 0
            elif self.estat in [7, 8]:
                if s_key == 'D':
                    self.estat += 1
                else:
                    self.estat = 0
            elif self.estat == 9:
                if self.sequence_mode == 'extended':
                    self.estat = 10
                else:  # 'standard'
                    self.estat = 99
                    self.m_oStrokeQueue.put(s_key)
            elif self.estat in [10, 11, 12, 13]:
                if s_key == 'A':
                    self.estat += 1
                else:
                    self.estat = 0
            elif self.estat == 14:
                self.estat = 99
                self.m_oStrokeQueue.put(s_key)

            transparent_estat_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] if self.sequence_mode == 'extended' else [0, 1, 2, 3, 4]
            return True if self.estat in transparent_estat_list else False
        except Exception as e:
            self.estat = 0
            self.last_time = 0
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return False

    def show_loading_icon(self):
        s_html = self.add_clock_overlay(self.s_html_last_sent)
        self.sio_emit_FP('kapri_ins_screen_html_document_write', s_html)

    def hide_loading_icon(self):
        s_html = self.s_html_last_sent
        self.sio_emit_FP('kapri_ins_screen_html_document_write', s_html)

    def set_guispy_sequence_mode(self, desired_sequence_mode):
        self.sequence_mode = 'extended' if desired_sequence_mode == 'extended' else 'standard'

    # ------ funcions internes de la classe

    def gui_thread_task(self):
        with self.app.app_context():
            # tecles B: BACK, C: UP, D: DOWN, A: OK
            while True:
                try:
                    s_key = self.m_oStrokeQueue.get()
                    if s_key == 'B':
                        self.reboot()
                    elif s_key == 'C':
                        self.shutdown()
                    elif s_key == 'D':
                        self.show_EUI_info()
                    elif s_key == 'A':
                        self.show_system_info()
                except Exception as e:
                    logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
                finally:
                    self.estat = 0

    def show_html_and_restore(self, s_html, show_time):
        self.sio_emit_FP('kapri_ins_screen_html_document_write', s_html)
        time.sleep(show_time)
        # restaurem la pantalla original
        if self.s_html_last_sent is not None:
            self.sio_emit_FP('kapri_ins_screen_html_document_write', self.s_html_last_sent)

    def show_system_info(self):
        info_dict = self.mgr_device_info.get_device_info_dict()
        # pàgina 1
        s_html = f"<h4>IP address:  ... </h4><h3>{info_dict.get('sIP_Address')}</h3>"
        s_html += f"<h4>MAC address: ... </h4><h3>{info_dict.get('sMAC_Address')}</h3>"
        s_html += f"<h4>sEUI64: ... </h4><h3>{info_dict.get('sEUI64_Carrier')}</h3>"
        self.show_html_and_restore(s_html, MgrGuispy.LONG_SHOW_TIME)
        # pàgina 2
        s_html = f"<h4>IP addressWLAN:  ... </h4><h3>{info_dict.get('sIP_AddressWLAN')}</h3>"
        s_html += f"<h4>MAC addressWLAN: ... </h4><h3>{info_dict.get('sMAC_AddressWLAN')}</h3>"
        s_html += f"<h4>Image Ver.: ... </h4><h3>{info_dict.get('sImageVersion')}</h3>"
        self.show_html_and_restore(s_html, MgrGuispy.LONG_SHOW_TIME)


    def show_EUI_info(self):
        info_dict = self.mgr_device_info.get_device_info_dict()
        # pàgina 1
        s_html = f"<h4>sEUI64 Carrier:  ... </h4><h3>{info_dict.get('sEUI64_Carrier')}</h3>"
        s_html += f"<h4>sEUI64 Lexa main: ... </h4><h3>{info_dict.get('sEUI64_LexaMain')}</h3>"
        s_html += f"<h4>sEUI64 Lexa aux: ... </h4><h3>{info_dict.get('sEUI64_LexaAux')}</h3>"
        self.show_html_and_restore(s_html, MgrGuispy.LONG_SHOW_TIME)
        # pàgina 2
        s_html = f"<h4>FwVer Carrier: ... </h4><h3>{info_dict.get('sFwVer_Carrier')}</h3>"
        s_html += f"<h4>FwVer LexaMain: ... </h4><h3>{info_dict.get('sFwVer_LexaMain')}</h3>"
        s_html += f"<h4>FwVer LexaAux: ... </h4><h3>{info_dict.get('sFwVer_LexaAux')}</h3>"
        self.show_html_and_restore(s_html, MgrGuispy.LONG_SHOW_TIME)

    def reboot(self):
        self.mgr_linuxsys.reboot()
        s_html = "<h1>Rebooting... </h1>"
        self.show_html_and_restore(s_html, MgrGuispy.LONG_SHOW_TIME)

    def shutdown(self):
        self.mgr_linuxsys.shutdown()
        s_html = "<h1>Shutting down... </h1>"
        self.show_html_and_restore(s_html, MgrGuispy.LONG_SHOW_TIME)

    def add_clock_overlay(self, html):
        icon_url = 'post_loading.png'
        overlay_style = "position: absolute; top: 40%; left: 30%; transform: translate(-50%, -50%) z-index: 9999;"
        icon_overlay = f"<div style='{overlay_style}'><img src='{icon_url}' height='40' width='40' alt='Clock Icon'></div>"
        modified_html = html + icon_overlay
        return modified_html