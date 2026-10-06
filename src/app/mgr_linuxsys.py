# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
import logging

from app.ktp_ret import KtpRet
from app.post_woman import PostWoman


class MgrLinuxsys:

    def __init__(self, app, mgr_hardware_info, mgr_kapriassist):
        self.app = app
        self.mgr_hardware_info = mgr_hardware_info
        self.mgr_kapriassist = mgr_kapriassist

    def reboot(self):
        try:
            ucRet = KtpRet.RET_OK
            # Hot Reset Carrier
            params = f"/api/nodes/{self.mgr_hardware_info.get('sEUI64')}/Cpu/HotReset"
            my_url = self.app.config['URL']['url_kxphostproapi'] + params
            result = PostWoman.send_get(my_url)
            if result.get('ucInsRet') != 0:
                ucRet = KtpRet.RET_FAILED
            # Hot Reset Lexa Main
            if self.mgr_hardware_info.get('sEUI64_LexaMain') is not None:
                params = f"/api/nodes/{self.mgr_hardware_info.get('sEUI64_LexaMain')}/Cpu/HotReset"
                my_url = self.app.config['URL']['url_kxphostproapi'] + params
                result = PostWoman.send_get(my_url)
                if result.get('ucInsRet') != 0:
                    ucRet = KtpRet.RET_FAILED
            # Hot Reset Lexa Aux
            if self.mgr_hardware_info.get('sEUI64_LexaAux') is not None:
                params = f"/api/nodes/{self.mgr_hardware_info.get('sEUI64_LexaAux')}/Cpu/HotReset"
                my_url = self.app.config['URL']['url_kxphostproapi'] + params
                result = PostWoman.send_get(my_url)
                if result.get('ucInsRet') != 0:
                    ucRet = KtpRet.RET_FAILED
            # Reboot físic del Nanopi
            resu = self.mgr_kapriassist.RebootNanopi()
            if resu != 'OK':
                ucRet = KtpRet.RET_FAILED
            return ucRet
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_EXCEPTION

    def shutdown(self):
        try:
            ucRet = KtpRet.RET_OK
            # Shutdown físic del Nanopi
            resu = self.mgr_kapriassist.ShutdownNanopi()
            if resu != 'OK':
                ucRet = KtpRet.RET_FAILED
            return ucRet
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_EXCEPTION

    def get_dt_utc_timezone(self):
        try:
            ucRet = KtpRet.RET_OK
            # GET DATE TIME UTC
            resu, device_dt_utc, local_timezone = self.mgr_kapriassist.get_dt_utc_timezone()
            if resu != 'OK':
                ucRet = KtpRet.RET_FAILED
            return ucRet, device_dt_utc, local_timezone
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_EXCEPTION, None, None

    def set_dt_utc(self, device_dt_utc):
        try:
            ucRet = KtpRet.RET_OK
            # SET DATE TIME UTC
            resu = self.mgr_kapriassist.set_dt_utc(device_dt_utc)
            if resu != 'OK':
                ucRet = KtpRet.RET_FAILED
            return ucRet
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_EXCEPTION

    def scan_wifi(self):
        try:
            ucRet = KtpRet.RET_FAILED
            ssid_list = None
            # SCAN WIFI
            resu, llSSIDs = self.mgr_kapriassist.scan_wifi()
            if resu == 'OK':
                ucRet = KtpRet.RET_OK
                ssid_list = []
                for element in llSSIDs:
                    ssid_list.append(
                        {
                            'in_use': element['IN-USE'].find('*') >= 0,
                            'bssid': element['BSSID'],
                            'ssid': element['SSID'],
                            'channel': element['CHAN'],
                            'baud_rate': element['RATE'],
                            'signal': element['SIGNAL'],
                            'security': element['SECURITY']
                        }
                    )
            return ucRet, ssid_list
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return KtpRet.RET_EXCEPTION, None
