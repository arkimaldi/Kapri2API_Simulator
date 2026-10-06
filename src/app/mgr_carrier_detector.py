# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import time
import inspect
import logging

from app.global_consts import GlobalConsts
from app.config_translator import ConfigTranslator


class MgrCarrierDetector:
    # infinits retries per detectar la Carrier
    PERIPHERAL_DETECTION_RETRY_COUNTER_MAX = 15      # reintents per detectar els lexas esperats després de detectar la carrier

    def __init__(self, app, mgr_hardware_info, mgr_kxphost, mgr_config_carrier, mgr_config_lexamain, mgr_config_lexaaux):
        self.app = app
        self.mgr_hardware_info = mgr_hardware_info
        self.mgr_kxphost = mgr_kxphost
        self.mgr_config_carrier = mgr_config_carrier
        self.mgr_config_lexamain = mgr_config_lexamain
        self.mgr_config_lexaaux = mgr_config_lexaaux

    def detect(self):
        try:
            # Esbrinem quins periferics esperem detectar
            b_lexamain_expected, b_lexaaux_expected = self.get_expected_peripherals()
            # Esperem comunicació amb la KxpHostProAPIAPI-Carrier i obtenim EUIs de la Carrier i dels Lexas
            b_exit = False
            peripheral_detection_retry_counter = MgrCarrierDetector.PERIPHERAL_DETECTION_RETRY_COUNTER_MAX
            b_carrier_detected = False
            b_lexamain_detected = False
            b_lexaaux_detected = False
            sEUI64 = None
            sEUI64_LexaMain = None
            sEUI64_LexaAux = None
            while not b_exit:
                time.sleep(1)
                list_of_nodes = self.mgr_kxphost.get_nodes_list()
                if list_of_nodes is not None:
                    for node in list_of_nodes:
                        if 'ucKNet_Id' in node.keys():
                            if node['ucKNet_Id'] in [GlobalConsts.get('const_knet_id_kapri')]:
                                sEUI64 = node['sEUI64']
                                b_carrier_detected = True
                            elif node['ucKNet_Id'] in [GlobalConsts.get('const_knet_id_lexa')]:
                                if node['ucRange'] == 1:
                                    sEUI64_LexaMain = node['sEUI64']
                                    b_lexamain_detected = True
                                elif node['ucRange'] == 2:
                                    sEUI64_LexaAux = node['sEUI64']
                                    b_lexaaux_detected = True
                # anàlisi de la condició de sortida
                if b_carrier_detected:
                    if MgrCarrierDetector.is_peripheral_detection_complete(b_lexamain_detected, b_lexaaux_detected,
                                                                           b_lexamain_expected, b_lexaaux_expected):
                        b_exit = True
                    else:
                        peripheral_detection_retry_counter -= 1
                        if peripheral_detection_retry_counter == 0:
                            b_exit = True
            self.mgr_hardware_info.set('sEUI64', sEUI64)
            self.mgr_hardware_info.set('sEUI64_LexaMain', sEUI64_LexaMain)
            self.mgr_hardware_info.set('sEUI64_LexaAux', sEUI64_LexaAux)
            logging.info(f"Detecting carrier with EUI64 .... {sEUI64}")
            logging.info(f"Detecting lexa main with EUI64 .... {sEUI64_LexaMain}")
            logging.info(f"Detecting lexa aux with EUI64 .... {sEUI64_LexaAux}")
            # Obtenim la configuració dels diferents elements del hardware
            # Obtindrem configuració de la carrier
            sCfg1, sCfg2, sCfg3 = self.mgr_kxphost.get_configuration_hardware('carrier')
            dict_params = ConfigTranslator.kapri_translate_to_high_level(sCfg1, sCfg2, sCfg3)
            # Escribim a BBDDD els valors llegits des de la KxpHostProAPIAPI
            self.mgr_config_carrier.write(dict_params, 'current')
            # Aqui xequejarem si cal omplir les configs del Lexa Main i del Lexa Aux
            if sEUI64_LexaMain is not None:
                sCfg1, sCfg2, sCfg3 = self.mgr_kxphost.get_configuration_hardware('lexa_main')
                dict_params = ConfigTranslator.lexamain_translate_to_high_level(sCfg1, sCfg2, sCfg3)
                # Escribim a BBDDD els valors llegits des de la KxpHostProAPIAPI
                self.mgr_config_lexamain.write(dict_params, 'current')
            if sEUI64_LexaAux  is not None:
                sCfg1, sCfg2, sCfg3 = self.mgr_kxphost.get_configuration_hardware('lexa_aux')
                dict_params = ConfigTranslator.lexaaux_translate_to_high_level(sCfg1, sCfg2, sCfg3)
                # Escribim a BBDDD els valors llegits des de la KxpHostProAPIAPI
                self.mgr_config_lexaaux.write(dict_params, 'current')
            # Obtenim les versions dels diferents elements del hardware
            # fw version carrier
            sFwVer_Carrier = self.mgr_kxphost.get_fwversion_hardware('carrier')
            self.mgr_hardware_info.set('sFwVer_Carrier', sFwVer_Carrier)
            # fw version lexas
            if sEUI64_LexaMain is not None:
                sFwVer_LexaMain = self.mgr_kxphost.get_fwversion_hardware('lexa_main')
                self.mgr_hardware_info.set('sFwVer_LexaMain', sFwVer_LexaMain)
            if sEUI64_LexaAux is not None:
                sFwVer_LexaAux = self.mgr_kxphost.get_fwversion_hardware('lexa_aux')
                self.mgr_hardware_info.set('sFwVer_LexaAux', sFwVer_LexaAux)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def get_expected_peripherals(self):
        b_lexamain_expected = True  # per defecte esperem lexa main
        b_lexaaux_expected = True   # per defecte esperem lexa aux
        try:
            dict_params = self.mgr_config_carrier.read_current()
            b_lexamain_expected = True if dict_params['cfg_sci2_mode'] == 'kxp_main' else False
            b_lexaaux_expected = True if dict_params['cfg_sci1_mode'] == 'kxp_aux' else False
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            return b_lexamain_expected, b_lexaaux_expected

    @staticmethod
    def is_peripheral_detection_complete(b_lexamain_detected, b_lexaaux_detected,
                                         b_lexamain_expected, b_lexaaux_expected):
        # analitzem hardwares perifèrics detectats segons el que esperem
        b_lexamain_ok = False
        b_lexaaux_ok = False
        if (not b_lexamain_expected) or (b_lexamain_expected and b_lexamain_detected):
            b_lexamain_ok = True
        if (not b_lexaaux_expected) or (b_lexaaux_expected and b_lexaaux_detected):
            b_lexaaux_ok = True
        # avaluem resultat
        return b_lexamain_ok and b_lexaaux_ok


