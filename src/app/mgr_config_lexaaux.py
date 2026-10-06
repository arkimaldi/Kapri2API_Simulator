# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
import json
import logging

from k_check import KCheck
from app.ktp_ret import KtpRet
from app.utilities import Utils
from app.extensions import db
from app.db_models import LexaAuxConfiguration
from app.config_translator import ConfigTranslator


class MgrConfigLexaAux:

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
            lexaaux_configuration_qry = db.session.query(LexaAuxConfiguration).filter(LexaAuxConfiguration.id == rec_id).first()
            if lexaaux_configuration_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION
            if which == 'current':
                lexaaux_configuration_qry.init_all_to_none()
            if dict_params.get('aux_din_echo_0') is not None:
                param_failed = 'aux_din_echo_0'
                lexaaux_configuration_qry.aux_din_echo_0 = KCheck.booleanValue(dict_params['aux_din_echo_0'])
            if dict_params.get('aux_din_echo_1') is not None:
                param_failed = 'aux_din_echo_1'
                lexaaux_configuration_qry.aux_din_echo_1 = KCheck.booleanValue(dict_params['aux_din_echo_1'])
            if dict_params.get('aux_mif_host_fe') is not None:
                param_failed = 'aux_mif_host_fe'
                lexaaux_configuration_qry.aux_mif_host_fe = KCheck.elementInList(dict_params['aux_mif_host_fe'], ['J1', 'J2'])
            if dict_params.get('aux_mif_mode') is not None:
                param_failed = 'aux_mif_mode'
                lexaaux_configuration_qry.aux_mif_mode = KCheck.elementInList(dict_params['aux_mif_mode'], ['disabled', 'atqa_uid', 'one_block', 'three_blocks', 'desfire_file', 'multisector', 'reversed_atqa_uid', 'mad_one_block', 'mad_three_blocks'])
            if dict_params.get('aux_mif_block_number') is not None:
                param_failed = 'aux_mif_block_number'
                lexaaux_configuration_qry.aux_mif_block_number = KCheck.integerInInterval(dict_params['aux_mif_block_number'], 0, 255)
            if dict_params.get('aux_mif_login_mode') is not None:
                param_failed = 'aux_mif_login_mode'
                lexaaux_configuration_qry.aux_mif_login_mode = KCheck.elementInList(dict_params['aux_mif_login_mode'], ['never', 'always', 'auto'])
            if dict_params.get('aux_mif_key_ab') is not None:
                param_failed = 'aux_mif_key_ab'
                lexaaux_configuration_qry.aux_mif_key_ab = KCheck.elementInList(dict_params['aux_mif_key_ab'], ['keya_isoauth', 'keyb_natauth'])
            if dict_params.get('aux_mif_key_number') is not None:
                param_failed = 'aux_mif_key_number'
                lexaaux_configuration_qry.aux_mif_key_number = KCheck.integerInInterval(dict_params['aux_mif_key_number'], 0, 23)
            if dict_params.get('aux_mif_read_ok_led_mode') is not None:
                param_failed = 'aux_mif_read_ok_led_mode'
                lexaaux_configuration_qry.aux_mif_read_ok_led_mode = KCheck.elementInList(dict_params['aux_mif_read_ok_led_mode'], ['off', 'on', 'flash_30', 'flash_50', 'flash_70'])
            if dict_params.get('aux_mif_read_ok_led_color') is not None:
                param_failed = 'aux_mif_read_ok_led_color'
                lexaaux_configuration_qry.aux_mif_read_ok_led_color = KCheck.elementInList(dict_params['aux_mif_read_ok_led_color'], ['black', 'red', 'green', 'orange', 'blue', 'purple', 'cyan', 'white'])
            if dict_params.get('aux_mif_read_ok_led_time_on_10ms') is not None:
                param_failed = 'aux_mif_read_ok_led_time_on_10ms'
                lexaaux_configuration_qry.aux_mif_read_ok_led_time_on_10ms = KCheck.integerInInterval(dict_params['aux_mif_read_ok_led_time_on_10ms'], 0, 255)
            if dict_params.get('aux_mif_read_fail_led_mode') is not None:
                param_failed = 'aux_mif_read_fail_led_mode'
                lexaaux_configuration_qry.aux_mif_read_fail_led_mode = KCheck.elementInList(dict_params['aux_mif_read_fail_led_mode'], ['off', 'on', 'flash_30', 'flash_50', 'flash_70'])
            if dict_params.get('aux_mif_read_fail_led_color') is not None:
                param_failed = 'aux_mif_read_fail_led_color'
                lexaaux_configuration_qry.aux_mif_read_fail_led_color = KCheck.elementInList(dict_params['aux_mif_read_fail_led_color'], ['black', 'red', 'green', 'orange', 'blue', 'purple', 'cyan', 'white'])
            if dict_params.get('aux_mif_read_fail_led_time_on_10ms') is not None:
                param_failed = 'aux_mif_read_fail_led_time_on_10ms'
                lexaaux_configuration_qry.aux_mif_read_fail_led_time_on_10ms = KCheck.integerInInterval(dict_params['aux_mif_read_fail_led_time_on_10ms'], 0, 255)
            if dict_params.get('aux_mif_read_ok_bzz_mode') is not None:
                param_failed = 'aux_mif_read_ok_bzz_mode'
                lexaaux_configuration_qry.aux_mif_read_ok_bzz_mode = KCheck.elementInList(dict_params['aux_mif_read_ok_bzz_mode'], ['off', 'on', 'beep_30', 'beep_50', 'beep_70'])
            if dict_params.get('aux_mif_read_ok_bzz_time_on_10ms') is not None:
                param_failed = 'aux_mif_read_ok_bzz_time_on_10ms'
                lexaaux_configuration_qry.aux_mif_read_ok_bzz_time_on_10ms = KCheck.integerInInterval(dict_params['aux_mif_read_ok_bzz_time_on_10ms'], 0, 255)
            if dict_params.get('aux_mif_read_fail_bzz_mode') is not None:
                param_failed = 'aux_mif_read_fail_bzz_mode'
                lexaaux_configuration_qry.aux_mif_read_fail_bzz_mode = KCheck.elementInList(dict_params['aux_mif_read_fail_bzz_mode'], ['off', 'on', 'beep_30', 'beep_50', 'beep_70'])
            if dict_params.get('aux_mif_read_fail_bzz_time_on_10ms') is not None:
                param_failed = 'aux_mif_read_fail_bzz_time_on_10ms'
                lexaaux_configuration_qry.aux_mif_read_fail_bzz_time_on_10ms = KCheck.integerInInterval(dict_params['aux_mif_read_fail_bzz_time_on_10ms'], 0, 255)
            if dict_params.get('aux_mif_inter_instruction_tmo_10ms') is not None:
                param_failed = 'aux_mif_inter_instruction_tmo_10ms'
                lexaaux_configuration_qry.aux_mif_inter_instruction_tmo_10ms = KCheck.integerInInterval(dict_params['aux_mif_inter_instruction_tmo_10ms'], 20, 255)
            if dict_params.get('aux_mif_field_off_duration_10ms') is not None:
                param_failed = 'aux_mif_field_off_duration_10ms'
                lexaaux_configuration_qry.aux_mif_field_off_duration_10ms = KCheck.integerInInterval(dict_params['aux_mif_field_off_duration_10ms'], 20, 255)
            if dict_params.get('aux_mif_keep_field_on_time_ds') is not None:
                param_failed = 'aux_mif_keep_field_on_time_ds'
                lexaaux_configuration_qry.aux_mif_keep_field_on_time_ds = KCheck.integerInInterval(dict_params['aux_mif_keep_field_on_time_ds'], 2, 255)
            if dict_params.get('aux_mif_rx_gain') is not None:
                param_failed = 'aux_mif_rx_gain'
                lexaaux_configuration_qry.aux_mif_rx_gain = KCheck.elementInList(dict_params['aux_mif_rx_gain'], ['30db', '40db', '50db', '60db'])
            if dict_params.get('aux_mif_msector_sel') is not None:
                param_failed = 'aux_mif_msector_sel'
                lexaaux_configuration_qry.aux_mif_msector_sel = MgrConfigLexaAux.check_mif_msector_sel(dict_params['aux_mif_msector_sel'])
            if dict_params.get('aux_mif_msector_keyab') is not None:
                param_failed = 'aux_mif_msector_keyab'
                lexaaux_configuration_qry.aux_mif_msector_keyab = MgrConfigLexaAux.check_mif_msector_keyab(
                    dict_params['aux_mif_msector_keyab'])
            db.session.add(lexaaux_configuration_qry)
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
            # llegim DDBB
            lexaaux_configuration_1_qry = db.session.query(LexaAuxConfiguration).filter(LexaAuxConfiguration.id == 1).one()
            dict_config_1 = Utils.get_qry_dict(lexaaux_configuration_1_qry)
            if 'id' in dict_config_1.keys():
                del dict_config_1['id']
            lexaaux_configuration_2_qry = db.session.query(LexaAuxConfiguration).filter(LexaAuxConfiguration.id == 2).one()
            dict_config_2 = Utils.get_qry_dict(lexaaux_configuration_2_qry)
            db.session.close()
            if 'id' in dict_config_2.keys():
                del dict_config_2['id']
            # obtenim el diccionari dels canvis de configuració i
            dict_config_different = {}
            for k, v in dict_config_2.items():
                if v != dict_config_1[k]:
                    dict_config_different[k] = v
            # Si canvia un DIN, respectem els valors que tenien la resta de DINs
            if dict_config_different.get('aux_din_echo_0') is not None or \
                dict_config_different.get('aux_din_echo_1') is not None:
                if dict_config_different.get('aux_din_echo_0') is None:
                    dict_config_different['aux_din_echo_0'] = dict_config_1['aux_din_echo_0']
                if dict_config_different.get('aux_din_echo_1') is None:
                    dict_config_different['aux_din_echo_1'] = dict_config_1['aux_din_echo_1']
            # apliquem canvis, si n'hi ha
            if len(dict_config_different) > 0:
                d_f1, d_f2, d_f3 = ConfigTranslator.lexaaux_translate_to_low_level(dict_config_different)
                # EEPROM 1
                for k, v in d_f1.items():
                    if v is not None:
                        if not self.mgr_kxphost.set_configuration_hardware_one_parameter(sEUI64=self.mgr_hardware_info.get('sEUI64_LexaAux'), ucEepromNumber=1, uiParameterIdx=k, ucParameterValue=str(int(v, 16))):
                            ucRet = KtpRet.RET_FAILED
                            break
                '''
                La EEPROM2 no canviarà mai, ja que conté els parametres Ethernet que en Kapri no apliquen
                if ucRet == KtpRet.RET_OK:
                    for k, v in d_f2.items():
                        if v is not None:
                            if not self.mgr_kxphost.set_configuration_hardware_one_parameter(sEUI64=self.mgr_hardware_info.get('sEUI64_LexaAux'), ucEepromNumber=2, uiParameterIdx=k, ucParameterValue=str(int(v, 16))):
                                ucRet = KtpRet.RET_FAILED
                                break
                '''
                # EEPROM 3
                if ucRet == KtpRet.RET_OK:
                    for k, v in d_f3.items():
                        if v is not None:
                            if not self.mgr_kxphost.set_configuration_hardware_one_parameter(sEUI64=self.mgr_hardware_info.get('sEUI64_LexaAux'), ucEepromNumber=3, uiParameterIdx=k, ucParameterValue=str(int(v, 16))):
                                ucRet = KtpRet.RET_FAILED
                                break
                if ucRet == KtpRet.RET_OK:
                    if not self.mgr_kxphost.store_and_reset_configuration_hardware(sEUI64=self.mgr_hardware_info.get('sEUI64_LexaAux')):
                        ucRet = KtpRet.RET_FAILED
                if ucRet == KtpRet.RET_OK:
                    # Obtindrem configuració de la lexa auxiliar
                    sCfg1, sCfg2, sCfg3 = self.mgr_kxphost.get_configuration_hardware('lexa_aux')
                    dict_params = ConfigTranslator.lexaaux_translate_to_high_level(sCfg1, sCfg2, sCfg3)
                    # Escribim a BBDDD els valors llegits des de la KxpHostProAPIAPI
                    self.write(dict_params, 'current')
            return ucRet, False
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.close()
            return KtpRet.RET_EXCEPTION, False

    def read_future(self):
        dict_config = None
        b_config_apply_needed = False
        dict_apply_diffs = {}
        try:
            # Llegim la ultima configuració gravada
            lexaaux_configuration_2_qry = db.session.query(LexaAuxConfiguration).filter(LexaAuxConfiguration.id == 2).one()
            dict_config = Utils.get_qry_dict(lexaaux_configuration_2_qry)
            if 'id' in dict_config.keys():
                del dict_config['id']
            # Llegim configuració activa del sistema, per saber si és diferent de la nova que ens han gravat
            # Comparem configuracions gravada a BBDD i la activa (sense id )
            lexaaux_configuration_1_qry = db.session.query(LexaAuxConfiguration).filter(LexaAuxConfiguration.id == 1).one()
            aux_dict_activa = Utils.get_qry_dict(lexaaux_configuration_1_qry)
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

    def backup_future(self):
        try:
            lexaaux_configuration_2_qry = db.session.query(LexaAuxConfiguration).filter(LexaAuxConfiguration.id == 2).first()
            lexaaux_configuration_3_qry = db.session.query(LexaAuxConfiguration).filter(LexaAuxConfiguration.id == 3).first()
            if lexaaux_configuration_2_qry is None or lexaaux_configuration_3_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION

            lexaaux_configuration_3_qry.aux_din_echo_0 = lexaaux_configuration_2_qry.aux_din_echo_0
            lexaaux_configuration_3_qry.aux_din_echo_1 = lexaaux_configuration_2_qry.aux_din_echo_1
            lexaaux_configuration_3_qry.aux_mif_host_fe = lexaaux_configuration_2_qry.aux_mif_host_fe
            lexaaux_configuration_3_qry.aux_mif_mode = lexaaux_configuration_2_qry.aux_mif_mode
            lexaaux_configuration_3_qry.aux_mif_block_number = lexaaux_configuration_2_qry.aux_mif_block_number
            lexaaux_configuration_3_qry.aux_mif_login_mode = lexaaux_configuration_2_qry.aux_mif_login_mode
            lexaaux_configuration_3_qry.aux_mif_key_ab = lexaaux_configuration_2_qry.aux_mif_key_ab
            lexaaux_configuration_3_qry.aux_mif_key_number = lexaaux_configuration_2_qry.aux_mif_key_number
            lexaaux_configuration_3_qry.aux_mif_read_ok_led_mode = lexaaux_configuration_2_qry.aux_mif_read_ok_led_mode
            lexaaux_configuration_3_qry.aux_mif_read_ok_led_color = lexaaux_configuration_2_qry.aux_mif_read_ok_led_color
            lexaaux_configuration_3_qry.aux_mif_read_ok_led_time_on_10ms = lexaaux_configuration_2_qry.aux_mif_read_ok_led_time_on_10ms
            lexaaux_configuration_3_qry.aux_mif_read_fail_led_mode = lexaaux_configuration_2_qry.aux_mif_read_fail_led_mode
            lexaaux_configuration_3_qry.aux_mif_read_fail_led_color = lexaaux_configuration_2_qry.aux_mif_read_fail_led_color
            lexaaux_configuration_3_qry.aux_mif_read_fail_led_time_on_10ms = lexaaux_configuration_2_qry.aux_mif_read_fail_led_time_on_10ms
            lexaaux_configuration_3_qry.aux_mif_read_ok_bzz_mode = lexaaux_configuration_2_qry.aux_mif_read_ok_bzz_mode
            lexaaux_configuration_3_qry.aux_mif_read_ok_bzz_time_on_10ms = lexaaux_configuration_2_qry.aux_mif_read_ok_bzz_time_on_10ms
            lexaaux_configuration_3_qry.aux_mif_read_fail_bzz_mode = lexaaux_configuration_2_qry.aux_mif_read_fail_bzz_mode
            lexaaux_configuration_3_qry.aux_mif_read_fail_bzz_time_on_10ms = lexaaux_configuration_2_qry.aux_mif_read_fail_bzz_time_on_10ms
            lexaaux_configuration_3_qry.aux_mif_inter_instruction_tmo_10ms = lexaaux_configuration_2_qry.aux_mif_inter_instruction_tmo_10ms
            lexaaux_configuration_3_qry.aux_mif_field_off_duration_10ms = lexaaux_configuration_2_qry.aux_mif_field_off_duration_10ms
            lexaaux_configuration_3_qry.aux_mif_keep_field_on_time_ds = lexaaux_configuration_2_qry.aux_mif_keep_field_on_time_ds
            lexaaux_configuration_3_qry.aux_mif_rx_gain = lexaaux_configuration_2_qry.aux_mif_rx_gain
            lexaaux_configuration_3_qry.aux_mif_msector_sel = lexaaux_configuration_2_qry.aux_mif_msector_sel
            lexaaux_configuration_3_qry.aux_mif_msector_keyab = lexaaux_configuration_2_qry.aux_mif_msector_keyab

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
            lexaaux_configuration_2_qry = db.session.query(LexaAuxConfiguration).filter(LexaAuxConfiguration.id == 2).first()
            lexaaux_configuration_3_qry = db.session.query(LexaAuxConfiguration).filter(LexaAuxConfiguration.id == 3).first()
            if lexaaux_configuration_2_qry is None or lexaaux_configuration_3_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION

            lexaaux_configuration_2_qry.aux_din_echo_0 = lexaaux_configuration_3_qry.aux_din_echo_0
            lexaaux_configuration_2_qry.aux_din_echo_1 = lexaaux_configuration_3_qry.aux_din_echo_1
            lexaaux_configuration_2_qry.aux_mif_host_fe = lexaaux_configuration_3_qry.aux_mif_host_fe
            lexaaux_configuration_2_qry.aux_mif_mode = lexaaux_configuration_3_qry.aux_mif_mode
            lexaaux_configuration_2_qry.aux_mif_block_number = lexaaux_configuration_3_qry.aux_mif_block_number
            lexaaux_configuration_2_qry.aux_mif_login_mode = lexaaux_configuration_3_qry.aux_mif_login_mode
            lexaaux_configuration_2_qry.aux_mif_key_ab = lexaaux_configuration_3_qry.aux_mif_key_ab
            lexaaux_configuration_2_qry.aux_mif_key_number = lexaaux_configuration_3_qry.aux_mif_key_number
            lexaaux_configuration_2_qry.aux_mif_read_ok_led_mode = lexaaux_configuration_3_qry.aux_mif_read_ok_led_mode
            lexaaux_configuration_2_qry.aux_mif_read_ok_led_color = lexaaux_configuration_3_qry.aux_mif_read_ok_led_color
            lexaaux_configuration_2_qry.aux_mif_read_ok_led_time_on_10ms = lexaaux_configuration_3_qry.aux_mif_read_ok_led_time_on_10ms
            lexaaux_configuration_2_qry.aux_mif_read_fail_led_mode = lexaaux_configuration_3_qry.aux_mif_read_fail_led_mode
            lexaaux_configuration_2_qry.aux_mif_read_fail_led_color = lexaaux_configuration_3_qry.aux_mif_read_fail_led_color
            lexaaux_configuration_2_qry.aux_mif_read_fail_led_time_on_10ms = lexaaux_configuration_3_qry.aux_mif_read_fail_led_time_on_10ms
            lexaaux_configuration_2_qry.aux_mif_read_ok_bzz_mode = lexaaux_configuration_3_qry.aux_mif_read_ok_bzz_mode
            lexaaux_configuration_2_qry.aux_mif_read_ok_bzz_time_on_10ms = lexaaux_configuration_3_qry.aux_mif_read_ok_bzz_time_on_10ms
            lexaaux_configuration_2_qry.aux_mif_read_fail_bzz_mode = lexaaux_configuration_3_qry.aux_mif_read_fail_bzz_mode
            lexaaux_configuration_2_qry.aux_mif_read_fail_bzz_time_on_10ms = lexaaux_configuration_3_qry.aux_mif_read_fail_bzz_time_on_10ms
            lexaaux_configuration_2_qry.aux_mif_inter_instruction_tmo_10ms = lexaaux_configuration_3_qry.aux_mif_inter_instruction_tmo_10ms
            lexaaux_configuration_2_qry.aux_mif_field_off_duration_10ms = lexaaux_configuration_3_qry.aux_mif_field_off_duration_10ms
            lexaaux_configuration_2_qry.aux_mif_keep_field_on_time_ds = lexaaux_configuration_3_qry.aux_mif_keep_field_on_time_ds
            lexaaux_configuration_2_qry.aux_mif_rx_gain = lexaaux_configuration_3_qry.aux_mif_rx_gain
            lexaaux_configuration_2_qry.aux_mif_msector_sel = lexaaux_configuration_3_qry.aux_mif_msector_sel
            lexaaux_configuration_2_qry.aux_mif_msector_keyab = lexaaux_configuration_3_qry.aux_mif_msector_keyab

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
            lexaaux_configuration_2_qry = db.session.query(LexaAuxConfiguration).filter(LexaAuxConfiguration.id == 2).first()
            lexaaux_configuration_4_qry = db.session.query(LexaAuxConfiguration).filter(LexaAuxConfiguration.id == 4).first()
            if lexaaux_configuration_2_qry is None or lexaaux_configuration_4_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION

            lexaaux_configuration_4_qry.aux_din_echo_0 = lexaaux_configuration_2_qry.aux_din_echo_0
            lexaaux_configuration_4_qry.aux_din_echo_1 = lexaaux_configuration_2_qry.aux_din_echo_1
            lexaaux_configuration_4_qry.aux_mif_host_fe = lexaaux_configuration_2_qry.aux_mif_host_fe
            lexaaux_configuration_4_qry.aux_mif_mode = lexaaux_configuration_2_qry.aux_mif_mode
            lexaaux_configuration_4_qry.aux_mif_block_number = lexaaux_configuration_2_qry.aux_mif_block_number
            lexaaux_configuration_4_qry.aux_mif_login_mode = lexaaux_configuration_2_qry.aux_mif_login_mode
            lexaaux_configuration_4_qry.aux_mif_key_ab = lexaaux_configuration_2_qry.aux_mif_key_ab
            lexaaux_configuration_4_qry.aux_mif_key_number = lexaaux_configuration_2_qry.aux_mif_key_number
            lexaaux_configuration_4_qry.aux_mif_read_ok_led_mode = lexaaux_configuration_2_qry.aux_mif_read_ok_led_mode
            lexaaux_configuration_4_qry.aux_mif_read_ok_led_color = lexaaux_configuration_2_qry.aux_mif_read_ok_led_color
            lexaaux_configuration_4_qry.aux_mif_read_ok_led_time_on_10ms = lexaaux_configuration_2_qry.aux_mif_read_ok_led_time_on_10ms
            lexaaux_configuration_4_qry.aux_mif_read_fail_led_mode = lexaaux_configuration_2_qry.aux_mif_read_fail_led_mode
            lexaaux_configuration_4_qry.aux_mif_read_fail_led_color = lexaaux_configuration_2_qry.aux_mif_read_fail_led_color
            lexaaux_configuration_4_qry.aux_mif_read_fail_led_time_on_10ms = lexaaux_configuration_2_qry.aux_mif_read_fail_led_time_on_10ms
            lexaaux_configuration_4_qry.aux_mif_read_ok_bzz_mode = lexaaux_configuration_2_qry.aux_mif_read_ok_bzz_mode
            lexaaux_configuration_4_qry.aux_mif_read_ok_bzz_time_on_10ms = lexaaux_configuration_2_qry.aux_mif_read_ok_bzz_time_on_10ms
            lexaaux_configuration_4_qry.aux_mif_read_fail_bzz_mode = lexaaux_configuration_2_qry.aux_mif_read_fail_bzz_mode
            lexaaux_configuration_4_qry.aux_mif_read_fail_bzz_time_on_10ms = lexaaux_configuration_2_qry.aux_mif_read_fail_bzz_time_on_10ms
            lexaaux_configuration_4_qry.aux_mif_inter_instruction_tmo_10ms = lexaaux_configuration_2_qry.aux_mif_inter_instruction_tmo_10ms
            lexaaux_configuration_4_qry.aux_mif_field_off_duration_10ms = lexaaux_configuration_2_qry.aux_mif_field_off_duration_10ms
            lexaaux_configuration_4_qry.aux_mif_keep_field_on_time_ds = lexaaux_configuration_2_qry.aux_mif_keep_field_on_time_ds
            lexaaux_configuration_4_qry.aux_mif_rx_gain = lexaaux_configuration_2_qry.aux_mif_rx_gain
            lexaaux_configuration_4_qry.aux_mif_msector_sel = lexaaux_configuration_2_qry.aux_mif_msector_sel
            lexaaux_configuration_4_qry.aux_mif_msector_keyab = lexaaux_configuration_2_qry.aux_mif_msector_keyab

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
            lexaaux_configuration_2_qry = db.session.query(LexaAuxConfiguration).filter(LexaAuxConfiguration.id == 2).first()
            lexaaux_configuration_4_qry = db.session.query(LexaAuxConfiguration).filter(LexaAuxConfiguration.id == 4).first()
            if lexaaux_configuration_2_qry is None or lexaaux_configuration_4_qry is None:
                db.session.close()
                return KtpRet.RET_EXCEPTION

            lexaaux_configuration_2_qry.aux_din_echo_0 = lexaaux_configuration_4_qry.aux_din_echo_0
            lexaaux_configuration_2_qry.aux_din_echo_1 = lexaaux_configuration_4_qry.aux_din_echo_1
            lexaaux_configuration_2_qry.aux_mif_host_fe = lexaaux_configuration_4_qry.aux_mif_host_fe
            lexaaux_configuration_2_qry.aux_mif_mode = lexaaux_configuration_4_qry.aux_mif_mode
            lexaaux_configuration_2_qry.aux_mif_block_number = lexaaux_configuration_4_qry.aux_mif_block_number
            lexaaux_configuration_2_qry.aux_mif_login_mode = lexaaux_configuration_4_qry.aux_mif_login_mode
            lexaaux_configuration_2_qry.aux_mif_key_ab = lexaaux_configuration_4_qry.aux_mif_key_ab
            lexaaux_configuration_2_qry.aux_mif_key_number = lexaaux_configuration_4_qry.aux_mif_key_number
            lexaaux_configuration_2_qry.aux_mif_read_ok_led_mode = lexaaux_configuration_4_qry.aux_mif_read_ok_led_mode
            lexaaux_configuration_2_qry.aux_mif_read_ok_led_color = lexaaux_configuration_4_qry.aux_mif_read_ok_led_color
            lexaaux_configuration_2_qry.aux_mif_read_ok_led_time_on_10ms = lexaaux_configuration_4_qry.aux_mif_read_ok_led_time_on_10ms
            lexaaux_configuration_2_qry.aux_mif_read_fail_led_mode = lexaaux_configuration_4_qry.aux_mif_read_fail_led_mode
            lexaaux_configuration_2_qry.aux_mif_read_fail_led_color = lexaaux_configuration_4_qry.aux_mif_read_fail_led_color
            lexaaux_configuration_2_qry.aux_mif_read_fail_led_time_on_10ms = lexaaux_configuration_4_qry.aux_mif_read_fail_led_time_on_10ms
            lexaaux_configuration_2_qry.aux_mif_read_ok_bzz_mode = lexaaux_configuration_4_qry.aux_mif_read_ok_bzz_mode
            lexaaux_configuration_2_qry.aux_mif_read_ok_bzz_time_on_10ms = lexaaux_configuration_4_qry.aux_mif_read_ok_bzz_time_on_10ms
            lexaaux_configuration_2_qry.aux_mif_read_fail_bzz_mode = lexaaux_configuration_4_qry.aux_mif_read_fail_bzz_mode
            lexaaux_configuration_2_qry.aux_mif_read_fail_bzz_time_on_10ms = lexaaux_configuration_4_qry.aux_mif_read_fail_bzz_time_on_10ms
            lexaaux_configuration_2_qry.aux_mif_inter_instruction_tmo_10ms = lexaaux_configuration_4_qry.aux_mif_inter_instruction_tmo_10ms
            lexaaux_configuration_2_qry.aux_mif_field_off_duration_10ms = lexaaux_configuration_4_qry.aux_mif_field_off_duration_10ms
            lexaaux_configuration_2_qry.aux_mif_keep_field_on_time_ds = lexaaux_configuration_4_qry.aux_mif_keep_field_on_time_ds
            lexaaux_configuration_2_qry.aux_mif_rx_gain = lexaaux_configuration_4_qry.aux_mif_rx_gain
            lexaaux_configuration_2_qry.aux_mif_msector_sel = lexaaux_configuration_4_qry.aux_mif_msector_sel
            lexaaux_configuration_2_qry.aux_mif_msector_keyab = lexaaux_configuration_4_qry.aux_mif_msector_keyab

            db.session.commit()
            db.session.close()
            return KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.rollback()
            db.session.close()
            return KtpRet.RET_EXCEPTION

    @staticmethod
    def check_mif_msector_sel(s_mif_sector_sel):
        sectors_list = [x.strip() for x in s_mif_sector_sel.split(',') if x != '']
        if len(sectors_list) != 16:
            raise Exception('K_Mif_Msector_Sel_CheckError')
        for sector in sectors_list:
            KCheck.elementInList(sector, ['0', '1'])
        return ','.join(sector for sector in sectors_list)

    @staticmethod
    def check_mif_msector_keyab(s_mif_sector_keyab):
        keys_list = [x.strip().lower() for x in s_mif_sector_keyab.split(',') if x != '']
        if len(keys_list) != 16:
            raise Exception('K_Mif_Msector_Keyab_CheckError')
        for sector in keys_list:
            KCheck.elementInList(sector, ['a', 'b'])
        return ','.join(keyab for keyab in keys_list)