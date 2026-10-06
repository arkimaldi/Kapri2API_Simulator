# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
import json
import logging

from k_check import KCheck
from app.ktp_ret import KtpRet
from app.utilities import Utils
from app.extensions import db
from app.db_models import CarrierConfiguration
from app.config_translator import ConfigTranslator


class MgrConfigCarrier:

    def __init__(self, app, mgr_hardware_info, mgr_kxphost):
        self.app = app
        self.mgr_hardware_info = mgr_hardware_info
        self.mgr_kxphost = mgr_kxphost
        
    def write(self, dict_params, which):
        param_failed = None
        try:
            # La configuració amb id=2 és la futura un cop reinicialitzi el sistema
            if which == 'future':
                rec_id = 2
            elif which == 'current':
                rec_id = 1
            else:
                return KtpRet.RET_EXCEPTION, param_failed
            carrier_configuration_qry = db.session.query(CarrierConfiguration).filter(CarrierConfiguration.id == rec_id).first()
            if carrier_configuration_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION
            if which == 'current':
                carrier_configuration_qry.init_all_to_none()
            if dict_params.get('cfg_sci1_baud') is not None:
                param_failed = 'cfg_sci1_baud'
                cfg_sci1_baud = KCheck.elementInList(dict_params['cfg_sci1_baud'], [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200])
                carrier_configuration_qry.cfg_sci1_baud = cfg_sci1_baud
            if dict_params.get('cfg_sci2_baud') is not None:
                param_failed = 'cfg_sci2_baud'
                cfg_sci2_baud = KCheck.elementInList(dict_params['cfg_sci2_baud'], [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200])
                carrier_configuration_qry.cfg_sci2_baud = cfg_sci2_baud
            if dict_params.get('cfg_sci1_mode') is not None:
                param_failed = 'cfg_sci1_mode'
                carrier_configuration_qry.cfg_sci1_mode = KCheck.elementInList(dict_params['cfg_sci1_mode'], ['closed', 'kxp_aux', 'fim_main', 'uart_main', 'sfm_main'])
            if dict_params.get('cfg_sci2_mode') is not None:
                param_failed = 'cfg_sci2_mode'
                carrier_configuration_qry.cfg_sci2_mode = KCheck.elementInList(dict_params['cfg_sci2_mode'], ['closed', 'kxp_main', 'fim_aux', 'uart_aux', 'sfm_aux'])
            if dict_params.get('cfg_din_echo_0') is not None:
                param_failed = 'cfg_din_echo_0'
                carrier_configuration_qry.cfg_din_echo_0 = KCheck.booleanValue(dict_params['cfg_din_echo_0'])
            if dict_params.get('cfg_din_echo_1') is not None:
                param_failed = 'cfg_din_echo_1'
                carrier_configuration_qry.cfg_din_echo_1 = KCheck.booleanValue(dict_params['cfg_din_echo_1'])
            if dict_params.get('cfg_din_echo_2') is not None:
                param_failed = 'cfg_din_echo_2'
                carrier_configuration_qry.cfg_din_echo_2 = KCheck.booleanValue(dict_params['cfg_din_echo_2'])
            if dict_params.get('cfg_din_echo_3') is not None:
                param_failed = 'cfg_din_echo_3'
                carrier_configuration_qry.cfg_din_echo_3 = KCheck.booleanValue(dict_params['cfg_din_echo_3'])
            if dict_params.get('cfg_din_echo_4') is not None:
                param_failed = 'cfg_din_echo_4'
                carrier_configuration_qry.cfg_din_echo_4 = KCheck.booleanValue(dict_params['cfg_din_echo_4'])
            if dict_params.get('cfg_ttl0_mode') is not None:
                param_failed = 'cfg_ttl0_mode'
                carrier_configuration_qry.cfg_ttl0_mode = KCheck.elementInList(dict_params['cfg_ttl0_mode'], ['closed', 'aba_tk2', 'wiegand_26', 'wiegand_34', 'wiegand_free'])
            if dict_params.get('cfg_ttl1_mode') is not None:
                param_failed = 'cfg_ttl1_mode'
                carrier_configuration_qry.cfg_ttl1_mode = KCheck.elementInList(dict_params['cfg_ttl1_mode'], ['closed', 'aba_tk2', 'wiegand_26', 'wiegand_34', 'wiegand_free'])
            if dict_params.get('cfg_fim0_operating_baud') is not None:
                param_failed = 'cfg_fim0_operating_baud'
                cfg_fim0_operating_baud = KCheck.elementInList(dict_params['cfg_fim0_operating_baud'], [9600, 19200, 38400, 57600, 115200])
                carrier_configuration_qry.cfg_fim0_operating_baud = cfg_fim0_operating_baud
            if dict_params.get('cfg_fim1_operating_baud') is not None:
                param_failed = 'cfg_fim1_operating_baud'
                cfg_fim1_operating_baud = KCheck.elementInList(dict_params['cfg_fim1_operating_baud'], [9600, 19200, 38400, 57600, 115200])
                carrier_configuration_qry.cfg_fim1_operating_baud = cfg_fim1_operating_baud
            if dict_params.get('cfg_sfm0_operating_baud') is not None:
                param_failed = 'cfg_sfm0_operating_baud'
                cfg_sfm0_operating_baud = KCheck.elementInList(dict_params['cfg_sfm0_operating_baud'], [9600, 19200, 38400, 57600, 115200])
                carrier_configuration_qry.cfg_sfm0_operating_baud = cfg_sfm0_operating_baud
            if dict_params.get('cfg_sfm1_operating_baud') is not None:
                param_failed = 'cfg_sfm1_operating_baud'
                cfg_sfm1_operating_baud = KCheck.elementInList(dict_params['cfg_sfm1_operating_baud'], [9600, 19200, 38400, 57600, 115200])
                carrier_configuration_qry.cfg_sfm1_operating_baud = cfg_sfm1_operating_baud
            db.session.add(carrier_configuration_qry)
            db.session.commit()
            db.session.close()
            return KtpRet.RET_OK, None
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.rollback()
            db.session.close()
            return KtpRet.RET_INVALIDARGUMENT, param_failed

    def apply(self):
        try:
            ucRet = KtpRet.RET_OK
            b_reboot_needed = False
            # llegim DDBB
            carrier_configuration_1_qry = db.session.query(CarrierConfiguration).filter(CarrierConfiguration.id == 1).one()
            dict_config_1 = Utils.get_qry_dict(carrier_configuration_1_qry)
            if 'id' in dict_config_1.keys():
                del dict_config_1['id']
            carrier_configuration_2_qry = db.session.query(CarrierConfiguration).filter(CarrierConfiguration.id == 2).one()
            dict_config_2 = Utils.get_qry_dict(carrier_configuration_2_qry)
            db.session.close()
            if 'id' in dict_config_2.keys():
                del dict_config_2['id']
            # obtenim el diccionari dels canvis de configuració i
            # mirem si cal rebotar la nanopi per rearrencar la KxpHostProAPIAPI i refrescar la detecció de lexas
            dict_config_different = {}
            for k, v in dict_config_2.items():
                if  v != dict_config_1[k]:
                    dict_config_different[k] = v
                    if k in ['cfg_sci1_mode', 'cfg_sci2_mode']:
                        b_reboot_needed = True
            # Si canvia un DIN, respectem els valors que tenien la resta de DINs
            if dict_config_different.get('cfg_din_echo_0') is not None or \
                dict_config_different.get('cfg_din_echo_1') is not None or \
                dict_config_different.get('cfg_din_echo_2') is not None or \
                dict_config_different.get('cfg_din_echo_3') is not None or \
                dict_config_different.get('cfg_din_echo_4') is not None:
                if dict_config_different.get('cfg_din_echo_0') is None:
                    dict_config_different['cfg_din_echo_0'] = dict_config_1['cfg_din_echo_0']
                if dict_config_different.get('cfg_din_echo_1') is None:
                    dict_config_different['cfg_din_echo_1'] = dict_config_1['cfg_din_echo_1']
                if dict_config_different.get('cfg_din_echo_2') is None:
                    dict_config_different['cfg_din_echo_2'] = dict_config_1['cfg_din_echo_2']
                if dict_config_different.get('cfg_din_echo_3') is None:
                    dict_config_different['cfg_din_echo_3'] = dict_config_1['cfg_din_echo_3']
                if dict_config_different.get('cfg_din_echo_4') is None:
                    dict_config_different['cfg_din_echo_4'] = dict_config_1['cfg_din_echo_4']

            # apliquem canvis, si n'hi ha
            if len(dict_config_different) > 0:
                d_f1, d_f2, d_f3 = ConfigTranslator.kapri_translate_to_low_level(dict_config_different)
                # EEPROM 1
                for k, v in d_f1.items():
                    if v is not None:
                        if not self.mgr_kxphost.set_configuration_hardware_one_parameter(sEUI64=self.mgr_hardware_info.get('sEUI64'), ucEepromNumber=1, uiParameterIdx=k, ucParameterValue=str(int(v, 16))):
                            ucRet = KtpRet.RET_FAILED
                            break
                '''
                La EEPROM2 no canviarà mai, ja que conté els parametres Ethernet que en Kapri no apliquen
                if ucRet == KtpRet.RET_OK:
                    for k, v in d_f2.items():
                        if v is not None:
                            if not self.mgr_kxphost.set_configuration_hardware_one_parameter(sEUI64=self.mgr_hardware_info.get('sEUI64'), ucEepromNumber=2, uiParameterIdx=k, ucParameterValue=str(int(v, 16))):
                                ucRet = KtpRet.RET_FAILED
                                break
                '''
                # EEPROM 3
                if ucRet == KtpRet.RET_OK:
                    for k, v in d_f3.items():
                        if v is not None:
                            if not self.mgr_kxphost.set_configuration_hardware_one_parameter(sEUI64=self.mgr_hardware_info.get('sEUI64'), ucEepromNumber=3, uiParameterIdx=k, ucParameterValue=str(int(v, 16))):
                                ucRet = KtpRet.RET_FAILED
                                break
                if ucRet == KtpRet.RET_OK:
                    if not self.mgr_kxphost.store_and_reset_configuration_hardware(sEUI64=self.mgr_hardware_info.get('sEUI64')):
                        ucRet = KtpRet.RET_FAILED
                if ucRet == KtpRet.RET_OK:
                    # Obtindrem configuració de la carrier
                    sCfg1, sCfg2, sCfg3 = self.mgr_kxphost.get_configuration_hardware('carrier')
                    dict_params = ConfigTranslator.kapri_translate_to_high_level(sCfg1, sCfg2, sCfg3)
                    # Escribim a BBDDD els valors llegits des de la KxpHostProAPIAPI
                    self.write(dict_params, 'current')
            return ucRet, b_reboot_needed
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.close()
            return KtpRet.RET_EXCEPTION, False

    def read_future(self):
        dict_config = None
        b_config_apply_needed = False
        dict_apply_diffs = {}
        try:
            # Llegim la darrera configuració gravada
            carrier_configuration_2_qry = db.session.query(CarrierConfiguration).filter(CarrierConfiguration.id == 2).one()
            dict_config = Utils.get_qry_dict(carrier_configuration_2_qry)
            if 'id' in dict_config.keys():
                del dict_config['id']
            # Llegim configuració activa del sistema, per saber si és diferent de la nova que ens han gravat
            # Comparem configuracions gravades a BBDD i la activa (sense id )
            carrier_configuration_1_qry = db.session.query(CarrierConfiguration).filter(CarrierConfiguration.id == 1).one()
            aux_dict_activa = Utils.get_qry_dict(carrier_configuration_1_qry)
            if 'id' in aux_dict_activa.keys():
                del aux_dict_activa['id']
            dict_config_to_compare = json.loads(json.dumps(dict_config))
            for k, v in aux_dict_activa.items():
                if v is None:
                    dict_config_to_compare[k] = None
            if dict_config_to_compare != aux_dict_activa:
                b_config_apply_needed = True
                # documentem diferències
                for k, v in aux_dict_activa.items():
                    v_to_apply = dict_config_to_compare[k]
                    if v != v_to_apply:
                        dict_apply_diffs[k] = [v, v_to_apply]
        except Exception as e:
            dict_config = None
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            db.session.close()
            return b_config_apply_needed, dict_config, dict_apply_diffs

    def read_current(self):
        dict_config = None
        try:
            # Llegim configuració activa del sistema
            carrier_configuration_1_qry = db.session.query(CarrierConfiguration).filter(CarrierConfiguration.id == 1).one()
            dict_config = Utils.get_qry_dict(carrier_configuration_1_qry)
            if 'id' in dict_config.keys():
                del dict_config['id']
        except Exception as e:
            dict_config = None
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            db.session.close()
            return dict_config

    def backup_future(self):
        try:
            carrier_configuration_2_qry = db.session.query(CarrierConfiguration).filter(CarrierConfiguration.id == 2).first()
            carrier_configuration_3_qry = db.session.query(CarrierConfiguration).filter(CarrierConfiguration.id == 3).first()
            if carrier_configuration_2_qry is None or carrier_configuration_3_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION

            carrier_configuration_3_qry.cfg_sci1_baud = carrier_configuration_2_qry.cfg_sci1_baud
            carrier_configuration_3_qry.cfg_sci2_baud = carrier_configuration_2_qry.cfg_sci2_baud
            carrier_configuration_3_qry.cfg_sci1_mode = carrier_configuration_2_qry.cfg_sci1_mode
            carrier_configuration_3_qry.cfg_sci2_mode = carrier_configuration_2_qry.cfg_sci2_mode
            carrier_configuration_3_qry.cfg_din_echo_0 = carrier_configuration_2_qry.cfg_din_echo_0
            carrier_configuration_3_qry.cfg_din_echo_1 = carrier_configuration_2_qry.cfg_din_echo_1
            carrier_configuration_3_qry.cfg_din_echo_2 = carrier_configuration_2_qry.cfg_din_echo_2
            carrier_configuration_3_qry.cfg_din_echo_3 = carrier_configuration_2_qry.cfg_din_echo_3
            carrier_configuration_3_qry.cfg_din_echo_4 = carrier_configuration_2_qry.cfg_din_echo_4
            carrier_configuration_3_qry.cfg_ttl0_mode = carrier_configuration_2_qry.cfg_ttl0_mode
            carrier_configuration_3_qry.cfg_ttl1_mode = carrier_configuration_2_qry.cfg_ttl1_mode
            carrier_configuration_3_qry.cfg_fim0_operating_baud = carrier_configuration_2_qry.cfg_fim0_operating_baud
            carrier_configuration_3_qry.cfg_fim1_operating_baud = carrier_configuration_2_qry.cfg_fim1_operating_baud
            carrier_configuration_3_qry.cfg_sfm0_operating_baud = carrier_configuration_2_qry.cfg_sfm0_operating_baud
            carrier_configuration_3_qry.cfg_sfm1_operating_baud = carrier_configuration_2_qry.cfg_sfm1_operating_baud

            db.session.commit()
            db.session.close()
            return KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.rollback()
            db.session.close()
            return KtpRet.RET_EXCEPTION

    def restore_future(self):
        try:
            carrier_configuration_2_qry = db.session.query(CarrierConfiguration).filter(CarrierConfiguration.id == 2).first()
            carrier_configuration_3_qry = db.session.query(CarrierConfiguration).filter(CarrierConfiguration.id == 3).first()
            if carrier_configuration_2_qry is None or carrier_configuration_3_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION

            carrier_configuration_2_qry.cfg_sci1_baud = carrier_configuration_3_qry.cfg_sci1_baud
            carrier_configuration_2_qry.cfg_sci2_baud = carrier_configuration_3_qry.cfg_sci2_baud
            carrier_configuration_2_qry.cfg_sci1_mode = carrier_configuration_3_qry.cfg_sci1_mode
            carrier_configuration_2_qry.cfg_sci2_mode = carrier_configuration_3_qry.cfg_sci2_mode
            carrier_configuration_2_qry.cfg_din_echo_0 = carrier_configuration_3_qry.cfg_din_echo_0
            carrier_configuration_2_qry.cfg_din_echo_1 = carrier_configuration_3_qry.cfg_din_echo_1
            carrier_configuration_2_qry.cfg_din_echo_2 = carrier_configuration_3_qry.cfg_din_echo_2
            carrier_configuration_2_qry.cfg_din_echo_3 = carrier_configuration_3_qry.cfg_din_echo_3
            carrier_configuration_2_qry.cfg_din_echo_4 = carrier_configuration_3_qry.cfg_din_echo_4
            carrier_configuration_2_qry.cfg_ttl0_mode = carrier_configuration_3_qry.cfg_ttl0_mode
            carrier_configuration_2_qry.cfg_ttl1_mode = carrier_configuration_3_qry.cfg_ttl1_mode
            carrier_configuration_2_qry.cfg_fim0_operating_baud = carrier_configuration_3_qry.cfg_fim0_operating_baud
            carrier_configuration_2_qry.cfg_fim1_operating_baud = carrier_configuration_3_qry.cfg_fim1_operating_baud
            carrier_configuration_2_qry.cfg_sfm0_operating_baud = carrier_configuration_3_qry.cfg_sfm0_operating_baud
            carrier_configuration_2_qry.cfg_sfm1_operating_baud = carrier_configuration_3_qry.cfg_sfm1_operating_baud

            db.session.commit()
            db.session.close()
            return KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.rollback()
            db.session.close()
            return KtpRet.RET_EXCEPTION

    def backup_factory(self):
        try:
            carrier_configuration_2_qry = db.session.query(CarrierConfiguration).filter(CarrierConfiguration.id == 2).first()
            carrier_configuration_4_qry = db.session.query(CarrierConfiguration).filter(CarrierConfiguration.id == 4).first()
            if carrier_configuration_2_qry is None or carrier_configuration_4_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION

            carrier_configuration_4_qry.cfg_sci1_baud = carrier_configuration_2_qry.cfg_sci1_baud
            carrier_configuration_4_qry.cfg_sci2_baud = carrier_configuration_2_qry.cfg_sci2_baud
            carrier_configuration_4_qry.cfg_sci1_mode = carrier_configuration_2_qry.cfg_sci1_mode
            carrier_configuration_4_qry.cfg_sci2_mode = carrier_configuration_2_qry.cfg_sci2_mode
            carrier_configuration_4_qry.cfg_din_echo_0 = carrier_configuration_2_qry.cfg_din_echo_0
            carrier_configuration_4_qry.cfg_din_echo_1 = carrier_configuration_2_qry.cfg_din_echo_1
            carrier_configuration_4_qry.cfg_din_echo_2 = carrier_configuration_2_qry.cfg_din_echo_2
            carrier_configuration_4_qry.cfg_din_echo_3 = carrier_configuration_2_qry.cfg_din_echo_3
            carrier_configuration_4_qry.cfg_din_echo_4 = carrier_configuration_2_qry.cfg_din_echo_4
            carrier_configuration_4_qry.cfg_ttl0_mode = carrier_configuration_2_qry.cfg_ttl0_mode
            carrier_configuration_4_qry.cfg_ttl1_mode = carrier_configuration_2_qry.cfg_ttl1_mode
            carrier_configuration_4_qry.cfg_fim0_operating_baud = carrier_configuration_2_qry.cfg_fim0_operating_baud
            carrier_configuration_4_qry.cfg_fim1_operating_baud = carrier_configuration_2_qry.cfg_fim1_operating_baud
            carrier_configuration_4_qry.cfg_sfm0_operating_baud = carrier_configuration_2_qry.cfg_sfm0_operating_baud
            carrier_configuration_4_qry.cfg_sfm1_operating_baud = carrier_configuration_2_qry.cfg_sfm1_operating_baud

            db.session.commit()
            db.session.close()
            return KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.rollback()
            db.session.close()
            return KtpRet.RET_EXCEPTION

    def restore_factory(self):
        try:
            carrier_configuration_2_qry = db.session.query(CarrierConfiguration).filter(CarrierConfiguration.id == 2).first()
            carrier_configuration_4_qry = db.session.query(CarrierConfiguration).filter(CarrierConfiguration.id == 4).first()
            if carrier_configuration_2_qry is None or carrier_configuration_4_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION

            carrier_configuration_2_qry.cfg_sci1_baud = carrier_configuration_4_qry.cfg_sci1_baud
            carrier_configuration_2_qry.cfg_sci2_baud = carrier_configuration_4_qry.cfg_sci2_baud
            carrier_configuration_2_qry.cfg_sci1_mode = carrier_configuration_4_qry.cfg_sci1_mode
            carrier_configuration_2_qry.cfg_sci2_mode = carrier_configuration_4_qry.cfg_sci2_mode
            carrier_configuration_2_qry.cfg_din_echo_0 = carrier_configuration_4_qry.cfg_din_echo_0
            carrier_configuration_2_qry.cfg_din_echo_1 = carrier_configuration_4_qry.cfg_din_echo_1
            carrier_configuration_2_qry.cfg_din_echo_2 = carrier_configuration_4_qry.cfg_din_echo_2
            carrier_configuration_2_qry.cfg_din_echo_3 = carrier_configuration_4_qry.cfg_din_echo_3
            carrier_configuration_2_qry.cfg_din_echo_4 = carrier_configuration_4_qry.cfg_din_echo_4
            carrier_configuration_2_qry.cfg_ttl0_mode = carrier_configuration_4_qry.cfg_ttl0_mode
            carrier_configuration_2_qry.cfg_ttl1_mode = carrier_configuration_4_qry.cfg_ttl1_mode
            carrier_configuration_2_qry.cfg_fim0_operating_baud = carrier_configuration_4_qry.cfg_fim0_operating_baud
            carrier_configuration_2_qry.cfg_fim1_operating_baud = carrier_configuration_4_qry.cfg_fim1_operating_baud
            carrier_configuration_2_qry.cfg_sfm0_operating_baud = carrier_configuration_4_qry.cfg_sfm0_operating_baud
            carrier_configuration_2_qry.cfg_sfm1_operating_baud = carrier_configuration_4_qry.cfg_sfm1_operating_baud

            db.session.commit()
            db.session.close()
            return KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.rollback()
            db.session.close()
            return KtpRet.RET_EXCEPTION

