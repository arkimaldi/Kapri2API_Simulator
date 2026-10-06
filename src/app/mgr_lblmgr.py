# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import json


class MgrLblmgr:
    DATA_LEN_MAX = 1024

    def __init__(self, app):
        self.app =app
        #
        self.data = None

    def get_data(self):
        return self.data

    def set_data(self, data):
        b_ret = False
        try:
            if isinstance(data, dict):
                if len(json.dumps(data)) <= MgrLblmgr.DATA_LEN_MAX:
                    self.data = data
                    b_ret = True
        except:
            b_ret = False
        finally:
            return b_ret

    def clear_data(self):
        self.data = None