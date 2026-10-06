# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
import logging

from app.global_consts import GlobalConsts
from app.ktp_ret import KtpRet
from app.db_models import NanoConfiguration
from app.extensions import db


class MgrDeviceInfo:

    def __init__(self, app, mgr_hardware_info, mgr_kapriassist, mgr_knprxupdater):
        self.app = app
        self.mgr_hardware_info = mgr_hardware_info
        self.mgr_kapriassist = mgr_kapriassist
        self.mgr_knprxupdater = mgr_knprxupdater

    def get_device_info_dict(self):
        info_dict = {'ucRet': KtpRet.RET_FAILED,
                     'sDescription': '',
                     'ucModelNo': '',
                     'sName': '',
                     'sImageVersion': '',
                     'sSoftwareVersion': '',
                     'sFwVer_Carrier': '',
                     'sFwVer_LexaMain': '',
                     'sFwVer_LexaAux': '',
                     'sEUI64_Carrier': '',
                     'sEUI64_LexaMain': '',
                     'sEUI64_LexaAux': '',
                     'sMAC_Address': '',
                     'sMAC_AddressWLAN': '',
                     'sIP_Address': '',
                     'sIP_AddressWLAN': ''
                     }
        try:
            info_dict['ucModelNo'] = GlobalConsts.get('const_my_uc_model_no')
            info_dict['sName'] = GlobalConsts.get('const_my_sname')
            sImageVersion = self.mgr_knprxupdater.get_image_version()
            info_dict['sImageVersion'] = sImageVersion if sImageVersion is not None else ""
            info_dict['sSoftwareVersion'] = GlobalConsts.get('const_my_version')
            info_dict['sEUI64_Carrier'] = self.mgr_hardware_info.get('sEUI64') if self.mgr_hardware_info.get('sEUI64') is not None else ""
            info_dict['sEUI64_LexaMain'] = self.mgr_hardware_info.get('sEUI64_LexaMain') if self.mgr_hardware_info.get('sEUI64_LexaMain') is not None else ""
            info_dict['sEUI64_LexaAux'] = self.mgr_hardware_info.get('sEUI64_LexaAux') if self.mgr_hardware_info.get('sEUI64_LexaAux') is not None else ""
            info_dict['sMAC_Address'] = self.mgr_hardware_info.get('sMAC_Address') if self.mgr_hardware_info.get('sMAC_Address') != "Failed" else ""
            sMAC_AddressWLAN = self.mgr_kapriassist.get_wifi_mac_address()
            info_dict['sMAC_AddressWLAN'] =  sMAC_AddressWLAN if sMAC_AddressWLAN != "Failed" else ""
            sIP_Address = self.mgr_kapriassist.get_eth0_ip()
            info_dict['sIP_Address'] = sIP_Address if sIP_Address != "Failed" else ""
            sIP_AddressWLAN = self.mgr_kapriassist.get_wifi_ip()
            info_dict['sIP_AddressWLAN'] = sIP_AddressWLAN if sIP_AddressWLAN != "Failed" else ""
            info_dict['sFwVer_Carrier'] = self.mgr_hardware_info.get('sFwVer_Carrier') if self.mgr_hardware_info.get('sFwVer_Carrier') is not None else ""
            info_dict['sFwVer_LexaMain'] = self.mgr_hardware_info.get('sFwVer_LexaMain') if self.mgr_hardware_info.get('sFwVer_LexaMain') is not None else ""
            info_dict['sFwVer_LexaAux'] = self.mgr_hardware_info.get('sFwVer_LexaAux') if self.mgr_hardware_info.get('sFwVer_LexaAux') is not None else ""
            # terminal_name
            nano_configuration_1_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 1).first()
            if nano_configuration_1_qry is not None:
                info_dict['sDescription'] = nano_configuration_1_qry.terminal_description
            # ucRet
            info_dict['ucRet'] = KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            db.session.close()
            return info_dict
