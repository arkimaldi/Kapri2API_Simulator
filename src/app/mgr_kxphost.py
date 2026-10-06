# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import time

from app.post_woman import PostWoman


class MgrKxphost:

    def __init__(self, app, mgr_hardware_info):
        self.app = app
        self.mgr_hardware_info = mgr_hardware_info

    def get_nodes_list(self):
        try:
            my_url = self.app.config['URL']['url_kxphostproapi'] + '/api/nodes'
            listNodes = PostWoman.send_get(my_url)
            return listNodes
        except Exception as e:
            return None

    def get_configuration_hardware(self, s_boardname):
        sCfg1 = None
        sCfg2 = None
        sCfg3 = None
        if s_boardname == 'carrier':
            sEUI64 = self.mgr_hardware_info.get('sEUI64')
        elif s_boardname == 'lexa_main':
            sEUI64 = self.mgr_hardware_info.get('sEUI64_LexaMain')
        elif s_boardname == 'lexa_aux':
            sEUI64 = self.mgr_hardware_info.get('sEUI64_LexaAux')
        else:
            sEUI64 = ''
        while sCfg1 is None or sCfg2 is None or sCfg3 is None:
            sCfg1 = self.get_configuration_hardware_one_eeprom(sEUI64, 1)
            # EEPROM2 tot a FFs perque son valors Ethernet que aqui no apliquen
            # sCfg2 = get_configuration_hardware_one_eeprom(sEUI64, 2)
            sCfg2 = 0x40*'FF'
            sCfg3 = self.get_configuration_hardware_one_eeprom(sEUI64, 3)
            time.sleep(3)
        return sCfg1, sCfg2, sCfg3

    def get_configuration_hardware_one_eeprom(self, sEUI64, ucEepromNumber):
        sCfg = ''
        uiStartIdx = 0
        ucLen = 32
        my_url = self.app.config['URL']['url_kxphostproapi'] + f'/api/nodes/{sEUI64}/Cfg/Read/{ucEepromNumber}/{uiStartIdx}/{ucLen}'
        result = PostWoman.send_get(my_url)
        if result['ucInsRet'] != 0:
            return None
        else:
            sCfg = result['sParameters']
            uiStartIdx = 32
            ucLen = 32
            my_url = self.app.config['URL']['url_kxphostproapi'] + f'/api/nodes/{sEUI64}/Cfg/Read/{ucEepromNumber}/{uiStartIdx}/{ucLen}'
            result = PostWoman.send_get(my_url)
            if result['ucInsRet'] != 0:
                return None
            else:
                sCfg += result['sParameters']
        return sCfg

    def set_configuration_hardware_one_parameter(self, sEUI64, ucEepromNumber, uiParameterIdx, ucParameterValue):
        my_url = self.app.config['URL']['url_kxphostproapi'] + f'/api/nodes/{sEUI64}/Cfg/Write/{ucEepromNumber}/{uiParameterIdx}/{ucParameterValue}'
        result = PostWoman.send_get(my_url)
        if result['ucInsRet'] == 0:
            return True
        else:
            return False

    def store_and_reset_configuration_hardware(self, sEUI64):
        bRet = False
        my_url = self.app.config['URL']['url_kxphostproapi'] + f'/api/nodes/{sEUI64}/Cfg/Store'
        result = PostWoman.send_get(my_url)
        if result['ucInsRet'] == 0:
            my_url = self.app.config['URL']['url_kxphostproapi'] + f'/api/nodes/{sEUI64}/Cpu/HotReset'
            result = PostWoman.send_get(my_url)
            if result['ucInsRet'] == 0:
                bRet = True
        time.sleep(0.5)
        return bRet

    def get_fwversion_hardware(self, s_boardname):
        sVersion = None
        if s_boardname == 'carrier':
            sEUI64 = self.mgr_hardware_info.get('sEUI64')
        elif s_boardname == 'lexa_main':
            sEUI64 = self.mgr_hardware_info.get('sEUI64_LexaMain')
        elif s_boardname == 'lexa_aux':
            sEUI64 = self.mgr_hardware_info.get('sEUI64_LexaAux')
        else:
            sEUI64 = ''
        ucFlashNumber = 1
        params = f"/api/nodes/{sEUI64}/Cpu/GetFwVersion/{ucFlashNumber}"
        my_url = self.app.config['URL']['url_kxphostproapi'] + params
        result = PostWoman.send_get(my_url)
        if result.get('ucInsRet') == 0:
            sVersion = result.get('sVersion')
        return sVersion
