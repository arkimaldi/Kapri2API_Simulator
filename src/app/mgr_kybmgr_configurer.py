# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
import json
import logging

from app.db_models import NanoConfiguration
from app.extensions import db


class MgrKybmgrConfigurer:

    def __init__(self, app, mgr_kybmgr):
        self.app = app
        self.mgr_kybmgr = mgr_kybmgr

    def start(self):
        try:
            nano_configuration_1_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 1).first()
            if nano_configuration_1_qry is not None:
                desired_configuration = None
                if nano_configuration_1_qry.kybmgr_enabled:
                    try:
                        desired_configuration = json.loads(nano_configuration_1_qry.kybmgr_cfg_1)
                    except:
                        pass
                self.mgr_kybmgr.configure(desired_configuration)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            db.session.close()