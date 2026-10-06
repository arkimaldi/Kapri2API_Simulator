# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
import logging

from app.ktp_ret import KtpRet


class MgrConfigKapri:

    def __init__(self, app, mgr_hardware_info, mgr_kapriassist, mgr_config_nano, mgr_config_carrier, mgr_config_lexamain, mgr_config_lexaaux, mgr_web_users):
        self.app = app
        self.mgr_hardware_info = mgr_hardware_info
        self.mgr_kapriassist = mgr_kapriassist
        self.mgr_config_nano = mgr_config_nano
        self.mgr_config_carrier = mgr_config_carrier
        self.mgr_config_lexamain = mgr_config_lexamain
        self.mgr_config_lexaaux = mgr_config_lexaaux
        self.mgr_web_users = mgr_web_users

    def write_future(self, dict_params):
        param_failed = None
        try:
            ucRet, param_failed = self.mgr_config_nano.write_future(dict_params)
            if ucRet != KtpRet.RET_OK:
                return ucRet, param_failed
            ucRet, param_failed = self.mgr_config_carrier.write(dict_params, 'future')
            if ucRet != KtpRet.RET_OK:
                return ucRet, param_failed
            ucRet, param_failed = self.mgr_config_lexamain.write(dict_params, 'future')
            if ucRet != KtpRet.RET_OK:
                return ucRet, param_failed
            ucRet, param_failed = self.mgr_config_lexaaux.write(dict_params, 'future')
            if ucRet != KtpRet.RET_OK:
                return ucRet, param_failed
            return KtpRet.RET_OK, None
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_INVALIDARGUMENT, param_failed

    def apply(self):
        try:
            ucRet = KtpRet.RET_OK
            ucRet_nano, b_reboot_nano = self.mgr_config_nano.apply()
            ucRet_carrier, b_reboot_carrier = self.mgr_config_carrier.apply()
            if self.mgr_hardware_info.get('sEUI64_LexaMain') is not None:
                ucRet_lexamain, b_reboot_lexamain = self.mgr_config_lexamain.apply()
            else:
                ucRet_lexamain, b_reboot_lexamain = KtpRet.RET_OK, False
            if self.mgr_hardware_info.get('sEUI64_LexaAux') is not None:
                ucRet_lexaaux, b_reboot_lexaaux = self.mgr_config_lexaaux.apply()
            else:
                ucRet_lexaaux, b_reboot_lexaaux = KtpRet.RET_OK, False
            if ucRet_nano != KtpRet.RET_OK or ucRet_carrier != KtpRet.RET_OK or ucRet_lexamain != KtpRet.RET_OK or ucRet_lexaaux != KtpRet.RET_OK:
                ucRet = KtpRet.RET_FAILED
            if b_reboot_nano or b_reboot_carrier or b_reboot_lexamain or b_reboot_lexaaux:
                resu = self.mgr_kapriassist.RebootNanopi()
                if resu != 'OK':
                    ucRet = KtpRet.RET_FAILED
            return ucRet
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_EXCEPTION

    def read_future(self):
        dict_config = None
        b_config_modified = False
        dict_apply_diffs = {}
        try:
            b_nano_config_modified, dict_nano_config, dict_nano_apply_diffs = self.mgr_config_nano.read_future()
            b_carrier_config_modified, dict_carrier_config, dict_carrier_apply_diffs = self.mgr_config_carrier.read_future()
            b_lexa_main_config_modified, dict_lexa_main_config, dict_lexa_main_apply_diffs = self.mgr_config_lexamain.read_future()
            if self.mgr_hardware_info.get('sEUI64_LexaMain') is None:
                b_lexa_main_config_modified = False
            b_lexa_aux_config_modified, dict_lexa_aux_config, dict_lexa_aux_apply_diffs = self.mgr_config_lexaaux.read_future()
            if self.mgr_hardware_info.get('sEUI64_LexaAux') is None:
                b_lexa_aux_config_modified = False
            # calculem retorns: b_config_modified, dict_config, dict_apply_diffs
            b_config_modified = b_nano_config_modified or b_carrier_config_modified or b_lexa_main_config_modified or b_lexa_aux_config_modified
            dict_config = {**dict_nano_config, **dict_carrier_config, **dict_lexa_main_config, **dict_lexa_aux_config}
            if b_nano_config_modified:
                dict_apply_diffs = {**dict_apply_diffs, **dict_nano_apply_diffs}
            if b_carrier_config_modified:
                dict_apply_diffs = {**dict_apply_diffs, **dict_carrier_apply_diffs}
            if b_lexa_main_config_modified:
                dict_apply_diffs = {**dict_apply_diffs, **dict_lexa_main_apply_diffs}
            if b_lexa_aux_config_modified:
                dict_apply_diffs = {**dict_apply_diffs, **dict_lexa_aux_apply_diffs}
        except Exception as e:
            dict_config = None
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            return b_config_modified, dict_config, dict_apply_diffs

    def backup_future(self):
        try:
            ucRet = KtpRet.RET_OK
            ucRet_nano = self.mgr_config_nano.backup_future()
            ucRet_carrier = self.mgr_config_carrier.backup_future()
            ucRet_lexamain = self.mgr_config_lexamain.backup_future()
            ucRet_lexaaux = self.mgr_config_lexaaux.backup_future()
            if ucRet_nano != KtpRet.RET_OK or ucRet_carrier != KtpRet.RET_OK or ucRet_lexamain != KtpRet.RET_OK or ucRet_lexaaux != KtpRet.RET_OK:
                ucRet = KtpRet.RET_FAILED
            return ucRet
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_EXCEPTION

    def restore_future(self):
        try:
            ucRet = KtpRet.RET_OK
            ucRet_nano = self.mgr_config_nano.restore_future()
            ucRet_carrier = self.mgr_config_carrier.restore_future()
            ucRet_lexamain = self.mgr_config_lexamain.restore_future()
            ucRet_lexaaux = self.mgr_config_lexaaux.restore_future()
            if ucRet_nano != KtpRet.RET_OK or ucRet_carrier != KtpRet.RET_OK or ucRet_lexamain != KtpRet.RET_OK or ucRet_lexaaux != KtpRet.RET_OK:
                ucRet = KtpRet.RET_FAILED
            return ucRet
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_EXCEPTION

    def rollback_apply_diffs(self):
        ucRet = KtpRet.RET_FAILED
        try:
            b_config_modified, dict_config, dict_apply_diffs = self.read_future()
            if dict_config is None:
                raise
            if b_config_modified:
                dict_config_to_restore = {}
                for k, v in dict_apply_diffs.items():
                    dict_config_to_restore[k] = v[0]
                write_future_uc_ret, param_failed = self.write_future(dict_config_to_restore)
                if write_future_uc_ret != KtpRet.RET_OK:
                    raise Exception('Failed ' + param_failed)
            ucRet = KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_EXCEPTION
        finally:
            return ucRet

    def backup_factory(self):
        try:
            ucRet = KtpRet.RET_OK
            ucRet_nano = self.mgr_config_nano.backup_factory()
            ucRet_carrier = self.mgr_config_carrier.backup_factory()
            ucRet_lexamain = self.mgr_config_lexamain.backup_factory()
            ucRet_lexaaux = self.mgr_config_lexaaux.backup_factory()
            if ucRet_nano != KtpRet.RET_OK or ucRet_carrier != KtpRet.RET_OK or ucRet_lexamain != KtpRet.RET_OK or ucRet_lexaaux != KtpRet.RET_OK:
                ucRet = KtpRet.RET_FAILED
            return ucRet
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_EXCEPTION

    def restore_factory(self):
        try:
            ucRet = KtpRet.RET_OK
            ucRet_nano = self.mgr_config_nano.restore_factory()
            ucRet_carrier = self.mgr_config_carrier.restore_factory()
            ucRet_lexamain = self.mgr_config_lexamain.restore_factory()
            ucRet_lexaaux = self.mgr_config_lexaaux.restore_factory()
            if ucRet_nano != KtpRet.RET_OK or ucRet_carrier != KtpRet.RET_OK or ucRet_lexamain != KtpRet.RET_OK or ucRet_lexaaux != KtpRet.RET_OK:
                ucRet = KtpRet.RET_FAILED
            return ucRet
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_EXCEPTION

    def reset_factory(self):
        try:
            ucRet = self.restore_factory()
            if ucRet != KtpRet.RET_OK:
                return KtpRet.RET_FAILED

            if not self.mgr_web_users.reset_factory_credentials():
                return KtpRet.RET_FAILED

            ucRet = self.apply()
            return ucRet
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_EXCEPTION