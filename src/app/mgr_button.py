# (C) 2024 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import time
import queue
import threading
import inspect
import logging

from app.ktp_ret import KtpRet


class MgrButton:
    """
        Gestiona el botó físic de reset del terminal Kapri.

        Segons el temps que es manté polsat el botó, en alliberar-lo s'executa
        una acció diferent:

            < PRESSED_TIME_MIN (5 segons)                                       → ignorat, no es fa cap acció
            PRESSED_TIME_MIN .. < PRESSED_TIME_FACTORY  (entre 5 i 30 segons)   → network reset (torna la xarxa a DHCP)
            PRESSED_TIME_FACTORY .. PRESSED_TIME_ABORT (entre 30 i 60 segons)   → factory reset complet
            > PRESSED_TIME_ABORT                       (60 segons)              → cancel·lat (timeout de seguretat)
    """

    PRESSED_TIME_MIN = 5          # mínim temps que cal mantenir el botó polsat.
    PRESSED_TIME_FACTORY = 30     # llindar a partir del qual s'activa factory reset
    PRESSED_TIME_ABORT = 60       # timeout de seguretat: per sobre, es cancel·la


    def __init__(self, app, mgr_config_kapri, mgr_audit_logs):
        self.app = app
        self.mgr_config_kapri = mgr_config_kapri
        self.mgr_audit_logs = mgr_audit_logs
        #
        self.on_pressed_time = None
        self.sample_queue = queue.Queue()
        self.button_thread = None

    def start(self):
        self.button_thread = threading.Thread(target=self.button_thread_task, daemon=True)
        self.button_thread.start()

    def on_sample(self, pressed):
        self.sample_queue.put({'pressed': pressed, 'time': time.time()})

    # ------ funcions internes de la classe

    def button_thread_task(self):
        with self.app.app_context():
            while True:
                try:
                    sample = self.sample_queue.get()
                    if self.on_pressed_time is None:
                        if sample['pressed']:
                            # button pressed
                            self.on_pressed_time = sample['time']
                    else:
                        if not sample['pressed']:
                            # button released
                            elapsed = sample['time'] - self.on_pressed_time
                            if MgrButton.PRESSED_TIME_FACTORY <= elapsed <= MgrButton.PRESSED_TIME_ABORT:
                                self.do_factory_reset()
                            elif MgrButton.PRESSED_TIME_MIN <= elapsed < MgrButton.PRESSED_TIME_FACTORY:
                                self.do_network_reset()
                            self.on_pressed_time = None
                except Exception as e:
                    logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
                    self.on_pressed_time = None

    def do_network_reset(self):
        ucRet, param_failed = self.mgr_config_kapri.write_future({'network_dhcp_mode': 'DHCP'})
        if ucRet == KtpRet.RET_OK:
            ucRet = self.mgr_config_kapri.apply()
            if ucRet != KtpRet.RET_OK:
                logging.error(f'Network reset failed. Could not apply configuration')
        else:
            logging.error(f'Network reset failed. Could not write configuration')

    def do_factory_reset(self):
        ucRet = self.mgr_config_kapri.reset_factory()
        self.mgr_audit_logs.audit_log_write(
            self.mgr_audit_logs.AUDIT_VIA_BUTTON, user_name=None, ip=None,
            event=self.mgr_audit_logs.AUDIT_EVENT_CFG_FACTORY_RESET, ok=(ucRet == KtpRet.RET_OK)
        )
        if ucRet != KtpRet.RET_OK:
            logging.error(f'Factory reset failed. ucRet={ucRet}')