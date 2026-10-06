# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
import logging

from k_check import KCheck
from app.db_models import NanoConfiguration
from app.extensions import db


class MgrInterfaceGlobal:

    def __init__(self, app):
        self.app = app
        #
        self.interface_ins_pwd = None

    def get_interface_ins_pwd(self):
        return self.interface_ins_pwd

    def start(self):
        self.interface_ins_pwd = None
        try:
            # llegim el registre de la ddbb
            try:
                nano_configuration_1_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 1).one()
            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            else:
                # mirem si interface_ins_pwd està definida (string entre 1 i 500)
                try:
                    self.interface_ins_pwd = KCheck.stringLenInInterval(nano_configuration_1_qry.interface_ins_pwd, 1, 500)
                    logging.debug("interface_ins_pwd is set")
                except Exception as e:
                    logging.debug("interface_ins_pwd is NOT set")
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            db.session.close()
            logging.debug('cmd_start_interface')


