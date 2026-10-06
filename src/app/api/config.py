# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
from flask_restful import Resource
from flask_restful import reqparse, request
from flask import make_response
import json
import logging

from app.ktp_ret import KtpRet
from app.messages import Messages


class WriteFutureConfig(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        try:
            jso_ = request.get_json()
            parser = reqparse.RequestParser()
            parser.add_argument('terminal_description', type=str)

            parser.add_argument('rtc_local_timezone', type=str)

            parser.add_argument('network_ip_address', type=str)
            parser.add_argument('network_bits_mask', type=str)
            parser.add_argument('network_ip_router', type=str)
            parser.add_argument('network_dhcp_mode', type=str)

            parser.add_argument('wlan_enabled', type=bool)
            parser.add_argument('wlan_ssid', type=str)
            parser.add_argument('wlan_password', type=str)

            parser.add_argument('interface_ins_pwd', type=str)

            parser.add_argument('ktp_interface', type=bool)
            parser.add_argument('jso_interface', type=bool)
            parser.add_argument('http_interface', type=bool)
            parser.add_argument('cloud_interface', type=bool)

            parser.add_argument('ktp_server_client_mode', type=str)
            parser.add_argument('ktp_remote_server_ip_1', type=str)
            parser.add_argument('ktp_remote_server_ip_2', type=str)
            parser.add_argument('ktp_remote_server_port_1', type=int)
            parser.add_argument('ktp_remote_server_port_2', type=int)
            parser.add_argument('ktp_udp_detect', type=bool)
            parser.add_argument('ktp_udp_port', type=int)
            parser.add_argument('ktp_network_id', type=str)
            parser.add_argument('ktp_aes256', type=str)

            parser.add_argument('jso_server_client_mode', type=str)
            parser.add_argument('jso_remote_server_ip_1', type=str)
            parser.add_argument('jso_remote_server_port_1', type=int)
            parser.add_argument('jso_remote_server_ip_2', type=str)
            parser.add_argument('jso_remote_server_port_2', type=int)

            parser.add_argument('http_socketio_server_host', type=str)
            parser.add_argument('http_socketio_server_port', type=int)

            parser.add_argument('cloud_remote_server_url', type=str)
            parser.add_argument('cloud_remote_server_token', type=str)
            parser.add_argument('cloud_allowed_events', type=str)
            parser.add_argument('cloud_keep_alive_timeout', type=int)
            parser.add_argument('cloud_busy_relay', type=int)

            parser.add_argument('semi_offline_mode_enabled', type=bool)
            parser.add_argument('semi_offline_keep_alive_timeout', type=int)
            parser.add_argument('semi_offline_on_semi_offline_mode_enter_batch', type=str)
            parser.add_argument('semi_offline_on_usrtimer_elapsed_batch', type=str)
            parser.add_argument('semi_offline_on_mifare_track_batch', type=str)
            parser.add_argument('semi_offline_on_ttl_track_batch', type=str)
            parser.add_argument('semi_offline_on_fim_finger_batch', type=str)
            parser.add_argument('semi_offline_on_sfm_finger_batch', type=str)
            parser.add_argument('semi_offline_on_keyboard_echo_batch', type=str)
            parser.add_argument('semi_offline_on_uart_receive_batch', type=str)

            parser.add_argument('scankey_encoding', type=str)

            parser.add_argument('kybmgr_enabled', type=bool)
            parser.add_argument('kybmgr_cfg_1', type=str)

            parser.add_argument('screen_html_boot', type=str)

            # CARRIER
            parser.add_argument('cfg_sci1_baud', type=int)
            parser.add_argument('cfg_sci2_baud', type=int)
            parser.add_argument('cfg_sci1_mode', type=str)
            parser.add_argument('cfg_sci2_mode', type=str)
            parser.add_argument('cfg_din_echo_0', type=bool)
            parser.add_argument('cfg_din_echo_1', type=bool)
            parser.add_argument('cfg_din_echo_2', type=bool)
            parser.add_argument('cfg_din_echo_3', type=bool)
            parser.add_argument('cfg_din_echo_4', type=bool)
            parser.add_argument('cfg_ttl0_mode', type=str)
            parser.add_argument('cfg_ttl1_mode', type=str)
            parser.add_argument('cfg_fim0_operating_baud', type=int)
            parser.add_argument('cfg_fim1_operating_baud', type=int)
            parser.add_argument('cfg_sfm0_operating_baud', type=int)
            parser.add_argument('cfg_sfm1_operating_baud', type=int)

            # LEXA PRINCIPAL

            parser.add_argument('exp_din_echo_0', type=bool)
            parser.add_argument('exp_din_echo_1', type=bool)
            parser.add_argument('cfg_mif_host_fe', type=str)
            parser.add_argument('cfg_mif_mode', type=str)
            parser.add_argument('cfg_mif_block_number', type=int)
            parser.add_argument('cfg_mif_login_mode', type=str)
            parser.add_argument('cfg_mif_key_ab', type=str)
            parser.add_argument('cfg_mif_key_number', type=int)
            parser.add_argument('exp_mif_read_ok_led_mode', type=str)
            parser.add_argument('exp_mif_read_ok_led_color', type=str)
            parser.add_argument('exp_mif_read_ok_led_time_on_10ms', type=int)
            parser.add_argument('exp_mif_read_fail_led_mode', type=str)
            parser.add_argument('exp_mif_read_fail_led_color', type=str)
            parser.add_argument('exp_mif_read_fail_led_time_on_10ms', type=int)
            parser.add_argument('exp_mif_read_ok_bzz_mode', type=str)
            parser.add_argument('exp_mif_read_ok_bzz_time_on_10ms', type=int)
            parser.add_argument('exp_mif_read_fail_bzz_mode', type=str)
            parser.add_argument('exp_mif_read_fail_bzz_time_on_10ms', type=int)
            parser.add_argument('cfg_mif_inter_instruction_tmo_10ms', type=int)
            parser.add_argument('cfg_mif_field_off_duration_10ms', type=int)
            parser.add_argument('cfg_mif_keep_field_on_time_ds', type=int)
            parser.add_argument('cfg_mif_rx_gain', type=str)
            parser.add_argument('cfg_mif_msector_sel', type=str)
            parser.add_argument('cfg_mif_msector_keyab', type=str)

            # LEXA AUX
            parser.add_argument('aux_din_echo_0', type=bool)
            parser.add_argument('aux_din_echo_1', type=bool)
            parser.add_argument('aux_mif_host_fe', type=str)
            parser.add_argument('aux_mif_mode', type=str)
            parser.add_argument('aux_mif_block_number', type=int)
            parser.add_argument('aux_mif_login_mode', type=str)
            parser.add_argument('aux_mif_key_ab', type=str)
            parser.add_argument('aux_mif_key_number', type=int)
            parser.add_argument('aux_mif_read_ok_led_mode', type=str)
            parser.add_argument('aux_mif_read_ok_led_color', type=str)
            parser.add_argument('aux_mif_read_ok_led_time_on_10ms', type=int)
            parser.add_argument('aux_mif_read_fail_led_mode', type=str)
            parser.add_argument('aux_mif_read_fail_led_color', type=str)
            parser.add_argument('aux_mif_read_fail_led_time_on_10ms', type=int)
            parser.add_argument('aux_mif_read_ok_bzz_mode', type=str)
            parser.add_argument('aux_mif_read_ok_bzz_time_on_10ms', type=int)
            parser.add_argument('aux_mif_read_fail_bzz_mode', type=str)
            parser.add_argument('aux_mif_read_fail_bzz_time_on_10ms', type=int)
            parser.add_argument('aux_mif_inter_instruction_tmo_10ms', type=int)
            parser.add_argument('aux_mif_field_off_duration_10ms', type=int)
            parser.add_argument('aux_mif_keep_field_on_time_ds', type=int)
            parser.add_argument('aux_mif_rx_gain', type=str)
            parser.add_argument('aux_mif_msector_sel', type=str)
            parser.add_argument('aux_mif_msector_keyab', type=str)

            args = parser.parse_args()
            uc_ret, param_failed = self.kapri_app.mgr_config_kapri.write_future(args)
            self.kapri_app.mgr_audit_logs.audit_log_write(
                self.kapri_app.mgr_audit_logs.AUDIT_VIA_WEBADMIN, user_name=None, ip=None,
                event=self.kapri_app.mgr_audit_logs.AUDIT_EVENT_CFG_SAVE, ok=(uc_ret == KtpRet.RET_OK)
            )
            if uc_ret == KtpRet.RET_OK:
                return Messages.MSG_CONFIG_WRITE_FUTURE_OK
            else:
                raise Exception('Failed '+ param_failed)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_CONFIG_WRITE_FUTURE_ERROR


class ApplyConfig(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        try:
            uc_ret = self.kapri_app.mgr_config_kapri.apply()
            self.kapri_app.mgr_audit_logs.audit_log_write(
                self.kapri_app.mgr_audit_logs.AUDIT_VIA_WEBADMIN, user_name=None, ip=None,
                event=self.kapri_app.mgr_audit_logs.AUDIT_EVENT_CFG_APPLY, ok=(uc_ret == KtpRet.RET_OK)
            )
            if uc_ret != KtpRet.RET_OK:
                raise Exception('Apply KapriConfig FAILED')
            return Messages.MSG_CONFIG_APPLY_CURRENT_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_CONFIG_APPLY_CURRENT_ERROR


class ReadConfig(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def get(self):
        resp = None
        try:
            result = {'status_code': 400}
            b_config_modified, dict_config, dict_apply_diffs = self.kapri_app.mgr_config_kapri.read_future()
            if dict_config is not None:
                result = {'status_code': 200, 'b_config_modified': b_config_modified, 'dict_config_diffs': dict_apply_diffs, **dict_config}
            resp = make_response(json.dumps(result) )
            resp.headers['content-type'] = 'application/json'
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            return resp


class RollbackConfig(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        try:
            result = self.kapri_app.mgr_config_kapri.rollback_apply_diffs()
            if result != KtpRet.RET_OK:
                raise Exception('Rollback KapriConfig FAILED')
            return Messages.MSG_CONFIG_ROLLBACK_CURRENT_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_CONFIG_ROLLBACK_CURRENT_ERROR


class ConfigBackupRestore(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        try:
            jso_ = request.get_json()
            parser = reqparse.RequestParser()

            parser.add_argument('backup_or_restore', type=str)

            args = parser.parse_args()
            uc_ret = self.backup_or_restore(args)

            event = self.kapri_app.mgr_audit_logs.AUDIT_EVENT_CFG_BACKUP\
                if args['backup_or_restore'] == 'backup' \
                else self.kapri_app.mgr_audit_logs.AUDIT_EVENT_CFG_RESTORE
            self.kapri_app.mgr_audit_logs.audit_log_write(
                self.kapri_app.mgr_audit_logs.AUDIT_VIA_WEBADMIN, user_name=None, ip=None,
                event=event, ok=(uc_ret == KtpRet.RET_OK)
            )

            if uc_ret == KtpRet.RET_OK:
                if args['backup_or_restore'] == 'backup':
                    return Messages.MSG_CONFIG_BACKUP_OK
                elif args['backup_or_restore'] == 'restore':
                    return Messages.MSG_CONFIG_RESTORE_OK
            else:
                raise Exception('Failed ')
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_CONFIG_BACKUP_RESTORE_ERROR

    def backup_or_restore(self, dict_params):
        ucRet = KtpRet.RET_OK
        try:
            backup_or_restore = dict_params['backup_or_restore']
            if backup_or_restore == 'backup':
                ucRet = self.kapri_app.mgr_config_kapri.backup_future()
            elif backup_or_restore == 'restore':
                ucRet = self.kapri_app.mgr_config_kapri.restore_future()
            else:
                raise Exception('backup_or_restore undefined')
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_INVALIDARGUMENT
        finally:
            return ucRet


class ConfigFactoryReset(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('dummy', type=str, help='dummy')
            args = parser.parse_args()

            uc_ret = self.kapri_app.mgr_config_kapri.reset_factory()
            self.kapri_app.mgr_audit_logs.audit_log_write(self.kapri_app.mgr_audit_logs.AUDIT_VIA_WEBADMIN, user_name=None, ip=None,
                                      event=self.kapri_app.mgr_audit_logs.AUDIT_EVENT_CFG_FACTORY_RESET, ok=(uc_ret == KtpRet.RET_OK))
            if uc_ret == KtpRet.RET_OK:
                return Messages.MSG_FACTORY_RESET_OK
            else:
                raise Exception('Failed ')
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_FACTORY_RESET_ERROR
