# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import time
import inspect
import logging

from k_check import KCheck


class MgrNetwork:

    def __init__(self, app, mgr_hardware_info, mgr_kapriassist):
        self.app = app
        self.mgr_hardware_info = mgr_hardware_info
        self.mgr_kapriassist = mgr_kapriassist

    def start(self):
        logging.error(f'INFO MgrNetwork START.')
        while True:
            try:
                eth0_mac_address = self.mgr_kapriassist.get_eth0_mac_address()
                if KCheck.is_valid_mac_address(eth0_mac_address):
                    self.mgr_hardware_info.set('sMAC_Address', eth0_mac_address)
                    break
            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            time.sleep(1)
        logging.error(f"INFO MgrNetwork mac: {self.mgr_hardware_info.get('sMAC_Address')}")