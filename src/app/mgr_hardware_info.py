# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

class MgrHardwareInfo:

    def __init__(self):
        self.info_dict = {}
        self.clear()

    def clear(self):
        self.info_dict = {
            'sEUI64': None,
            'sEUI64_LexaMain': None,
            'sEUI64_LexaAux': None,
            'sMAC_Address': None,
            'sFwVer_Carrier': None,
            'sFwVer_LexaMain': None,
            'sFwVer_LexaAux': None,
        }

    def set(self, key, value):
        if key not in self.info_dict.keys():
            raise
        self.info_dict[key] = value

    def get(self, key):
        return self.info_dict[key]

