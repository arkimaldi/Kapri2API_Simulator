# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import datetime
from sqlalchemy import DateTime, Boolean, text

from app.extensions import db
from app.global_consts import GlobalConsts

# -------------------------------------------     NANOPI CONFIGURATION  -------------------------------------------

class NanoConfiguration(db.Model):
    __tablename__ = 'nano_configuration'

    id = db.Column(db.Integer, primary_key=True)
    terminal_description = db.Column(db.String(GlobalConsts.get('const_terminal_description_size')))   # longitud mínima const_terminal_description_lenmin

    rtc_local_timezone = db.Column(db.String(200))

    network_ip_address = db.Column(db.String(15))
    network_bits_mask = db.Column(db.Integer)
    network_ip_router = db.Column(db.String(15))
    network_dhcp_mode = db.Column(db.String(10))                                                 # Possibles valors: const_network_dhcp_mode_values

    wlan_enabled = db.Column(Boolean, default=False)
    wlan_ssid = db.Column(db.String(GlobalConsts.get('const_wlan_ssid_size')))                    # longitud mínima const_wlan_ssid_lenmin
    wlan_password = db.Column(db.String(GlobalConsts.get('const_wlan_password_size')))            # longitud mínima const_wlan_password_lenmin

    interface_ins_pwd = db.Column(db.String(GlobalConsts.get('const_interface_ins_pwd_size')))    # longitud mínima const_interface_ins_pwd_lenmin

    ktp_interface = db.Column(Boolean, default=False)
    jso_interface = db.Column(Boolean, default=False)
    http_interface = db.Column(Boolean, default=False)
    cloud_interface = db.Column(Boolean, default=False)

    ktp_server_client_mode = db.Column(db.String(10))                                             # Possibles valors: const_ktp_server_client_mode_values
    ktp_remote_server_ip_1 = db.Column(db.String(15))
    ktp_remote_server_ip_2 = db.Column(db.String(15))
    ktp_remote_server_port_1 = db.Column(db.Integer)
    ktp_remote_server_port_2 = db.Column(db.Integer)
    ktp_udp_detect = db.Column(Boolean, default=False)
    ktp_udp_port = db.Column(db.Integer)
    ktp_network_id = db.Column(db.String(GlobalConsts.get('const_ktp_network_id_size')))           # longitud mínima const_ktp_network_id_lenmin.
    ktp_aes256 = db.Column(db.String(GlobalConsts.get('const_ktp_aes256_size')))                   # només caracters HEXASCII

    jso_server_client_mode = db.Column(db.String(10))                                              # Possibles valors: const_jso_server_client_mode_values
    jso_remote_server_ip_1 = db.Column(db.String(15))
    jso_remote_server_port_1 = db.Column(db.Integer)
    jso_remote_server_ip_2 = db.Column(db.String(15))
    jso_remote_server_port_2 = db.Column(db.Integer)

    http_socketio_server_host = db.Column(db.String(15))
    http_socketio_server_port = db.Column(db.Integer)

    cloud_remote_server_url = db.Column(db.String(GlobalConsts.get('const_cloud_remote_server_url_size')))       # longitud mínima const_cloud_remote_server_url_lenmin
    cloud_remote_server_token = db.Column(db.String(GlobalConsts.get('const_cloud_remote_server_token_size')))   # longitud mínima const_cloud_remote_server_token_lenmin
    cloud_allowed_events = db.Column(db.String(GlobalConsts.get('const_cloud_allowed_events_size')))             # longitud mínima const_cloud_allowed_events_lenmin
    cloud_keep_alive_timeout = db.Column(db.Integer)
    cloud_busy_relay = db.Column(db.Integer, nullable=False, default=-1, server_default=text("-1"))              # valor per defecte -1: deshabilitat

    semi_offline_mode_enabled = db.Column(Boolean, default=False)
    semi_offline_keep_alive_timeout = db.Column(db.Integer)
    semi_offline_on_semi_offline_mode_enter_batch = db.Column(db.String(GlobalConsts.get('const_semi_offline_batch_size')))   # longitud mínima const_semi_offline_batch_lenmin
    semi_offline_on_usrtimer_elapsed_batch = db.Column(db.String(GlobalConsts.get('const_semi_offline_batch_size')))          # longitud mínima const_semi_offline_batch_lenmin
    semi_offline_on_mifare_track_batch = db.Column(db.String(GlobalConsts.get('const_semi_offline_batch_size')))              # longitud mínima const_semi_offline_batch_lenmin
    semi_offline_on_ttl_track_batch = db.Column(db.String(GlobalConsts.get('const_semi_offline_batch_size')))                 # longitud mínima const_semi_offline_batch_lenmin
    semi_offline_on_fim_finger_batch = db.Column(db.String(GlobalConsts.get('const_semi_offline_batch_size')))                # longitud mínima const_semi_offline_batch_lenmin
    semi_offline_on_sfm_finger_batch = db.Column(db.String(GlobalConsts.get('const_semi_offline_batch_size')))                # longitud mínima const_semi_offline_batch_lenmin
    semi_offline_on_keyboard_echo_batch = db.Column(db.String(GlobalConsts.get('const_semi_offline_batch_size')))             # longitud mínima const_semi_offline_batch_lenmin
    semi_offline_on_uart_receive_batch = db.Column(db.String(GlobalConsts.get('const_semi_offline_batch_size')))              # longitud mínima const_semi_offline_batch_lenmin

    scankey_encoding = db.Column(db.String(GlobalConsts.get('const_scankey_encoding_size')))                                      # Possibles valors: const_scankey_encoding_values

    kybmgr_enabled = db.Column(Boolean, default=False)
    kybmgr_cfg_1 = db.Column(db.String(GlobalConsts.get('const_kybmgr_cfg_1_size')))                                          # longitud mínima const_kybmgr_cfg_1_lenmin

    screen_html_boot = db.Column(db.String(GlobalConsts.get('const_screen_html_boot_size')))                                  # longitud mínima const_screen_html_boot_lenmin

# -------------------------------------------     CARRIER CONFIGURATION  -------------------------------------------


class CarrierConfiguration(db.Model):
    __tablename__ = 'carrier_configuration'

    id = db.Column(db.Integer, primary_key=True)
    cfg_sci1_baud = db.Column(db.Integer)
    cfg_sci2_baud = db.Column(db.Integer)
    cfg_sci1_mode = db.Column(db.String(15))
    cfg_sci2_mode = db.Column(db.String(15))
    cfg_din_echo_0 = db.Column(Boolean, default=True)
    cfg_din_echo_1 = db.Column(Boolean, default=True)
    cfg_din_echo_2 = db.Column(Boolean, default=True)
    cfg_din_echo_3 = db.Column(Boolean, default=True)
    cfg_din_echo_4 = db.Column(Boolean, default=True)
    cfg_ttl0_mode = db.Column(db.String(15))
    cfg_ttl1_mode = db.Column(db.String(15))
    cfg_fim0_operating_baud = db.Column(db.Integer)
    cfg_fim1_operating_baud = db.Column(db.Integer)
    cfg_sfm0_operating_baud = db.Column(db.Integer)
    cfg_sfm1_operating_baud = db.Column(db.Integer)

    def init_all_to_none(self):
        self.cfg_sci1_baud = None
        self.cfg_sci2_baud = None
        self.cfg_sci1_mode = None
        self.cfg_sci2_mode = None
        self.cfg_din_echo_0 = None
        self.cfg_din_echo_1 = None
        self.cfg_din_echo_2 = None
        self.cfg_din_echo_3 = None
        self.cfg_din_echo_4 = None
        self.cfg_ttl0_mode = None
        self.cfg_ttl1_mode = None
        self.cfg_fim0_operating_baud = None
        self.cfg_fim1_operating_baud = None
        self.cfg_sfm0_operating_baud = None
        self.cfg_sfm1_operating_baud = None

# -------------------------------------------     LEXA MAIN CONFIGURATION  -------------------------------------------


class LexaMainConfiguration(db.Model):
    __tablename__ = 'lexa_main_configuration'

    id = db.Column(db.Integer, primary_key=True)
    exp_din_echo_0 = db.Column(Boolean)
    exp_din_echo_1 = db.Column(Boolean)
    cfg_mif_host_fe = db.Column(db.String(3), nullable=False, default="J1", server_default=text("'J1'"))
    cfg_mif_mode = db.Column(db.String(20))
    cfg_mif_block_number = db.Column(db.Integer)
    cfg_mif_login_mode = db.Column(db.String(15))
    cfg_mif_key_ab = db.Column(db.String(15))
    cfg_mif_key_number = db.Column(db.Integer)
    exp_mif_read_ok_led_mode = db.Column(db.String(15))
    exp_mif_read_ok_led_color = db.Column(db.String(15))
    exp_mif_read_ok_led_time_on_10ms = db.Column(db.Integer)
    exp_mif_read_fail_led_mode = db.Column(db.String(15))
    exp_mif_read_fail_led_color = db.Column(db.String(15))
    exp_mif_read_fail_led_time_on_10ms = db.Column(db.Integer)
    exp_mif_read_ok_bzz_mode = db.Column(db.String(15))
    exp_mif_read_ok_bzz_time_on_10ms = db.Column(db.Integer)
    exp_mif_read_fail_bzz_mode = db.Column(db.String(15))
    exp_mif_read_fail_bzz_time_on_10ms = db.Column(db.Integer)
    cfg_mif_inter_instruction_tmo_10ms = db.Column(db.Integer)
    cfg_mif_field_off_duration_10ms = db.Column(db.Integer)
    cfg_mif_keep_field_on_time_ds = db.Column(db.Integer)
    cfg_mif_rx_gain = db.Column(db.String(15))
    cfg_mif_msector_sel = db.Column(db.String(32))
    cfg_mif_msector_keyab = db.Column(db.String(32))

    def init_all_to_none(self):
        self.exp_din_echo_0 = None
        self.exp_din_echo_1 = None
        self.cfg_mif_host_fe = None
        self.cfg_mif_mode = None
        self.cfg_mif_block_number = None
        self.cfg_mif_login_mode = None
        self.cfg_mif_key_ab = None
        self.cfg_mif_key_number = None
        self.exp_mif_read_ok_led_mode = None
        self.exp_mif_read_ok_led_color = None
        self.exp_mif_read_ok_led_time_on_10ms = None
        self.exp_mif_read_fail_led_mode = None
        self.exp_mif_read_fail_led_color = None
        self.exp_mif_read_fail_led_time_on_10ms = None
        self.exp_mif_read_ok_bzz_mode = None
        self.exp_mif_read_ok_bzz_time_on_10ms = None
        self.exp_mif_read_fail_bzz_mode = None
        self.exp_mif_read_fail_bzz_time_on_10ms = None
        self.cfg_mif_inter_instruction_tmo_10ms = None
        self.cfg_mif_field_off_duration_10ms = None
        self.cfg_mif_keep_field_on_time_ds = None
        self.cfg_mif_rx_gain = None
        self.cfg_mif_msector_sel = None
        self.cfg_mif_msector_keyab = None

# -------------------------------------------     LEXA AUXILIAR CONFIGURATION  -------------------------------------------


class LexaAuxConfiguration(db.Model):
    __tablename__ = 'lexa_aux_configuration'

    id = db.Column(db.Integer, primary_key=True)
    aux_din_echo_0 = db.Column(Boolean)
    aux_din_echo_1 = db.Column(Boolean)
    aux_mif_host_fe = db.Column(db.String(3), nullable=False, default="J1", server_default=text("'J1'"))
    aux_mif_mode = db.Column(db.String(20))
    aux_mif_block_number = db.Column(db.Integer)
    aux_mif_login_mode = db.Column(db.String(15))
    aux_mif_key_ab = db.Column(db.String(15))
    aux_mif_key_number = db.Column(db.Integer)
    aux_mif_read_ok_led_mode = db.Column(db.String(15))
    aux_mif_read_ok_led_color = db.Column(db.String(15))
    aux_mif_read_ok_led_time_on_10ms = db.Column(db.Integer)
    aux_mif_read_fail_led_mode = db.Column(db.String(15))
    aux_mif_read_fail_led_color = db.Column(db.String(15))
    aux_mif_read_fail_led_time_on_10ms = db.Column(db.Integer)
    aux_mif_read_ok_bzz_mode = db.Column(db.String(15))
    aux_mif_read_ok_bzz_time_on_10ms = db.Column(db.Integer)
    aux_mif_read_fail_bzz_mode = db.Column(db.String(15))
    aux_mif_read_fail_bzz_time_on_10ms = db.Column(db.Integer)
    aux_mif_inter_instruction_tmo_10ms = db.Column(db.Integer)
    aux_mif_field_off_duration_10ms = db.Column(db.Integer)
    aux_mif_keep_field_on_time_ds = db.Column(db.Integer)
    aux_mif_rx_gain = db.Column(db.String(15))
    aux_mif_msector_sel = db.Column(db.String(32))
    aux_mif_msector_keyab = db.Column(db.String(32))

    def init_all_to_none(self):
        self.aux_din_echo_0 = None
        self.aux_din_echo_1 = None
        self.aux_mif_host_fe = None
        self.aux_mif_mode = None
        self.aux_mif_block_number = None
        self.aux_mif_login_mode = None
        self.aux_mif_key_ab = None
        self.aux_mif_key_number = None
        self.aux_mif_read_ok_led_mode = None
        self.aux_mif_read_ok_led_color = None
        self.aux_mif_read_ok_led_time_on_10ms = None
        self.aux_mif_read_fail_led_mode = None
        self.aux_mif_read_fail_led_color = None
        self.aux_mif_read_fail_led_time_on_10ms = None
        self.aux_mif_read_ok_bzz_mode = None
        self.aux_mif_read_ok_bzz_time_on_10ms = None
        self.aux_mif_read_fail_bzz_mode = None
        self.aux_mif_read_fail_bzz_time_on_10ms = None
        self.aux_mif_inter_instruction_tmo_10ms = None
        self.aux_mif_field_off_duration_10ms = None
        self.aux_mif_keep_field_on_time_ds = None
        self.aux_mif_rx_gain = None
        self.aux_mif_msector_sel = None
        self.aux_mif_msector_keyab = None

# -------------------------------------------     USERS.PY    -------------------------------------------


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), index=True, unique=True)
    user_password_hash = db.Column(db.String(320))
    is_virgin = db.Column(Boolean, nullable=False, default=True, server_default=text("1"))

# -------------------------------------------     SEMI OFFLINE  -------------------------------------------


class SemiOfflineEvents(db.Model):
    __tablename__ = 'semi_offline_events'

    event_id = db.Column(db.Integer, primary_key=True)
    event_json = db.Column(db.String(GlobalConsts.get('const_semi_offline_event_json_size')))            # longitud mínima const_semi_offline_event_json_lenmin
    instruction_json = db.Column(db.String(GlobalConsts.get('const_semi_offline_event_json_size')))      # longitud mínima const_semi_offline_event_json_lenmin
    response_json = db.Column(db.String(GlobalConsts.get('const_semi_offline_event_json_size')))         # longitud mínima const_semi_offline_event_json_lenmin
    dt_utc = db.Column(DateTime, default=datetime.datetime.utcnow)


class SemiOfflineLists(db.Model):
    __tablename__ = 'semi_offline_lists'

    list_id = db.Column(db.Integer, primary_key=True)
    list_blob = db.Column(db.LargeBinary(length=GlobalConsts.get('const_semi_offline_list_blob_size')))  # longitud mínima  const_semi_offline_list_blob_lenmin, màxima const_semi_offline_list_blob_lenmax
    dt_utc = db.Column(DateTime, default=datetime.datetime.utcnow)


class AuditEntry(db.Model):
    __tablename__ = 'audit_entry'
    __table_args__ = {'sqlite_autoincrement': True}

    id = db.Column(db.Integer, primary_key=True)
    via = db.Column(db.String(15))
    user_name = db.Column(db.String(23))             # "" si no aplica
    ip = db.Column(db.String(15))                # "" si no aplica
    event = db.Column(db.String(23))
    result = db.Column(db.String(7))            # "ok" | "fail"
    dt_utc = db.Column(DateTime, default=datetime.datetime.utcnow)