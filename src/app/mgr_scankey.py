# (C) 2024 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
import logging

from app.db_models import NanoConfiguration
from app.extensions import db
from app.global_consts import GlobalConsts
from k_check import KCheck


class MgrScankey:
    MAP_R4X1 = {'A': 'B', 'B': 'A', 'C': 'D', 'D': 'C'}
    MAP_R4X4 = {'A': '7', 'B': '0', 'C': '9', 'D': '8', 'E': '4', 'F': '1', '0': 'B', '1': 'F', '2': '6', '3': '5', '4': 'E', '5': '3', '6': '2', '7': 'A', '8': 'D', '9': 'C'}

    def __init__(self, app):
        self.app = app
        # Propietats internes
        self.scankey_encoding = GlobalConsts.get('const_scankey_encoding_values')[0]

    def start(self):
        try:
            nano_configuration_1_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 1).first()
            if nano_configuration_1_qry is not None:
                if KCheck.elementInList(nano_configuration_1_qry.scankey_encoding, GlobalConsts.get('const_scankey_encoding_values')):
                    self.scankey_encoding = nano_configuration_1_qry.scankey_encoding
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            db.session.close()

    def decode(self, scan_code):
        if self.scankey_encoding == 'R4x1':
            return MgrScankey.MAP_R4X1.get(scan_code, scan_code)
        if self.scankey_encoding == 'R4x4':
            return MgrScankey.MAP_R4X4.get(scan_code, scan_code)
        else:  # 'D4x1', 'D4x4'
            return scan_code