# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
import logging

from app.post_woman import PostWoman


class MgrKapriassist:

    def __init__(self, app, mgr_hardware_info):
        self.app = app
        self.mgr_hardware_info = mgr_hardware_info
        
    def WriteEthernetInterfaceParameters(self, dhcp_mode, ip_address, bits_mask, ip_router):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi']
            if dhcp_mode == "DHCP":
                my_url += '/api/Os/Dhcp/Write'
            elif dhcp_mode == "Manual":
                ll_addbytes = ip_address.split('.')
                if len(ll_addbytes) != 4:
                    return "Failed"
                ll_routerbytes = ip_router.split('.')
                if len(ll_routerbytes) != 4:
                    return "Failed"
                my_url += f'/api/Os/FixedIp/Write/{ll_addbytes[0]}/{ll_addbytes[1]}/{ll_addbytes[2]}/{ll_addbytes[3]}/{bits_mask}/{ll_routerbytes[0]}/{ll_routerbytes[1]}/{ll_routerbytes[2]}/{ll_routerbytes[3]}'
            else:
                return "Error"
            result = PostWoman.send_get(my_url)
            if result.get('msgArg') is None:
                return "Failed"
            if result['msgArg'].get('ucInsRet') != 0:
                return "Failed"
            return "OK"
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return "Failed"

    def WriteWifiInterfaceParameters(self, wlan_enabled, wlan_ssid, wlan_password):
        try:
            if wlan_enabled:
                if self.activate_wifi(wlan_ssid, wlan_password):
                    return "OK"
            else:
                if self.deactivate_wifi():
                    return "OK"
            return "Failed"
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return "Failed"

    def RebootNanopi(self):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/Os/Reboot'
            result = PostWoman.send_get(my_url)
            if result.get('msgArg') is None:
                return "Failed"
            if result['msgArg'].get('ucInsRet') != 0:
                return "Failed"
            return "OK"
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return "Failed"

    def ShutdownNanopi(self):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/Os/Shutdown'
            result = PostWoman.send_get(my_url)
            if result.get('msgArg') is None:
                return "Failed"
            if result['msgArg'].get('ucInsRet') != 0:
                return "Failed"
            return "OK"
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return "Failed"

    def get_version(self):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/version'
            result = PostWoman.send_get(my_url)
            return result.get('sVersion')
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return None

    def get_dt_utc_timezone(self):
        device_dt_utc = None
        local_timezone = None
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/DtUtcTimezone/get'
            result = PostWoman.send_get(my_url)
            if result.get('msgArg') is None:
                return "Failed", device_dt_utc, local_timezone
            if result['msgArg'].get('ucInsRet') != 0:
                return "Failed", device_dt_utc, local_timezone
            return "OK", result['msgArg'].get('device_dt_utc'), result['msgArg'].get('local_timezone')
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return "Failed", device_dt_utc, local_timezone

    def set_dt_utc(self, device_dt_utc):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/DtUtc/set'
            my_dictio = {'device_dt_utc': device_dt_utc}
            result = PostWoman.send_post(my_url, my_dictio)
            if result.get('msgArg') is None:
                return "Failed"
            if result['msgArg'].get('ucInsRet') != 0:
                return "Failed"
            return "OK"
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return "Failed"

    def set_timezone(self, local_timezone):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/Timezone/set'
            my_dictio = {'local_timezone': local_timezone}
            result = PostWoman.send_post(my_url, my_dictio)
            if result.get('msgArg') is None:
                return "Failed"
            if result['msgArg'].get('ucInsRet') != 0:
                return "Failed"
            return "OK"
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return "Failed"


# -- ETHERNET

    def get_eth0_mac_address(self):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/Network/MacAddress/Eth0/Read'
            result = PostWoman.send_get(my_url)
            if result.get('msgArg') is None:
                return "Failed"
            if result['msgArg'].get('ucInsRet') != 0:
                return "Failed"
            s_mac = result['msgArg'].get('s_mac')
            if s_mac is not None:
                return s_mac
            else:
                return "Failed"
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return "Failed"

    def get_eth0_ip(self):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/Network/IP/Eth0/Read'
            result = PostWoman.send_get(my_url)
            if result.get('msgArg') is None:
                return "Failed"
            if result['msgArg'].get('ucInsRet') != 0:
                return "Failed"
            eth0_ip = result['msgArg'].get('eth0_ip')
            if eth0_ip is not None:
                return eth0_ip
            else:
                return "Failed"
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return "Failed"


# -- WIFI

    def get_wifi_mac_address(self):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/Network/MacAddress/Wifi/Read'
            result = PostWoman.send_get(my_url)
            if result.get('msgArg') is None:
                return "Failed"
            if result['msgArg'].get('ucInsRet') != 0:
                return "Failed"
            s_mac = result['msgArg'].get('s_mac')
            if s_mac is not None:
                return s_mac
            else:
                return "Failed"
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return "Failed"

    def get_wifi_ip(self):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/Network/IP/Wifi/Read'
            result = PostWoman.send_get(my_url)
            if result.get('msgArg') is None:
                return "Failed"
            if result['msgArg'].get('ucInsRet') != 0:
                return "Failed"
            wifi_ip = result['msgArg'].get('wifi_ip')
            if wifi_ip is not None:
                return wifi_ip
            else:
                return "Failed"
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return "Failed"

    def activate_wifi(self, ssid, password):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/Network/IP/Wifi/Activate'
            my_dictio = {'ssid': ssid, 'password': password}
            result = PostWoman.send_post(my_url, my_dictio)
            if result.get('msgArg') is None:
                return False
            if result['msgArg'].get('ucInsRet') != 0:
                return False
            else:
                return True
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return False

    def deactivate_wifi(self):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/Network/IP/Wifi/Deactivate'
            result = PostWoman.send_get(my_url)
            if result.get('msgArg') is None:
                return False
            if result['msgArg'].get('ucInsRet') != 0:
                return False
            else:
                return True
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return False

    def scan_wifi(self):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/Network/IP/Wifi/Scan'
            result = PostWoman.send_get(my_url)
            if result.get('msgArg') is None:
                return "Failed", None
            if result['msgArg'].get('ucInsRet') != 0:
                return "Failed", None
            return "OK", result['msgArg']['llSSIDs']
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return "Failed", None


    # -- SYSLOG

    def read_syslog(self, microservice):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + f'/api/Syslog/Read/{microservice}'
            result = PostWoman.send_get(my_url)
            if result.get('msgArg') is None:
                return False, '', ''
            if result['msgArg'].get('ucInsRet') != 0:
                return False, '', ''
            return True, result['msgArg']['response_systemctl'], result['msgArg']['response_journalctl']
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return False, '', ''

    # -- SSH

    def start_ssh(self):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/Ssh/Start'
            result = PostWoman.send_get(my_url)
            if result.get('msgArg') is None:
                return False
            if result['msgArg'].get('ucInsRet') != 0:
                return False
            return True
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return False

    def stop_ssh(self):
        try:
            my_url = self.app.config['URL']['url_kapriassistapi'] + '/api/Ssh/Stop'
            result = PostWoman.send_get(my_url)
            if result.get('msgArg') is None:
                return False
            if result['msgArg'].get('ucInsRet') != 0:
                return False
            return True
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return False
