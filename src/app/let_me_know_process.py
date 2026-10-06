# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
import time
import logging

from k_check import KCheck
from app.ktp_ret import KtpRet
from app.html_check import HtmlCheck
from app.post_woman import PostWoman


class LetMeKnowProcess:

    @staticmethod
    def process_event(kapri_app, msgType, msgArg):
        try:
            logging.debug(f'post_let_me_know_event {msgType}, {msgArg}')
            if msgType == 'on_something':
                logging.debug (f'Arriba un missatge del tipus { msgType}')
                # en un futur podriem processar events
            return ""
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return 'Error: '+ str(e)

    @staticmethod
    def process_instruction(kapri_app, msgType, msgArg):
        if LetMeKnowProcess.check_instruction_password(kapri_app, msgArg):
            sResult, dict_answer = LetMeKnowProcess.process_instruction_checked(kapri_app, msgType, msgArg)
        else:
            sResult, dict_answer = 'OK', {'ucRet': KtpRet.RET_INVALIDARGUMENT}
        return sResult, dict_answer

    @staticmethod
    def check_instruction_password(kapri_app, msgArg):
        try:
            if kapri_app.mgr_interface_global.get_interface_ins_pwd() is None:
                return True
            if msgArg['sInsPwd'] == kapri_app.mgr_interface_global.get_interface_ins_pwd():
                return True
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        return False

    @staticmethod
    def process_instruction_checked(kapri_app, msgType, msgArg):
        try:
            # --Elaborem diccionari de resposta en funció del tipus d'instrucció que ens demanen
            dict_answer = {'ucRet': KtpRet.RET_FAILED}
            try:
                # ####################################   CPU INSTRUCTIONS    #################
                # --  TEST NODE LINK
                if msgType == 'ins_cpu_test_node_link':
                    dict_answer = {'ucRet': KtpRet.RET_OK}
                # --LOOP BACK
                elif msgType == 'ins_cpu_loop_back':
                    dict_answer = {'ucRet': KtpRet.RET_OK, **msgArg}
                # -- HOT RESET
                elif msgType == 'ins_cpu_hot_reset':
                    ucRet = kapri_app.mgr_linuxsys.reboot()
                    dict_answer = {'ucRet': ucRet}
                # --SHUT DOWN
                elif msgType == 'ins_cpu_shutdown':
                    ucRet = kapri_app.mgr_linuxsys.shutdown()
                    dict_answer = {'ucRet': ucRet}
                # --GET DEVICE INFO
                elif msgType == 'ins_cpu_get_device_info':
                    dict_answer = kapri_app.mgr_device_info.get_device_info_dict()
                ### SCAN WIFI
                elif msgType == 'ins_cpu_scan_wifi':
                    ucRet, ssid_list = kapri_app.mgr_linuxsys.scan_wifi()
                    dict_answer = {'ucRet': ucRet}
                    if ucRet == KtpRet.RET_OK:
                        dict_answer['ssid_list'] = ssid_list

                # ####################################   CFG INSTRUCTIONS    #################
                # -- CFG READ
                elif msgType == 'ins_cfg_read':
                    b_config_modified, dict_config, dict_apply_diffs = kapri_app.mgr_config_kapri.read_future()
                    if dict_config is None:
                        dict_answer = {'ucRet': KtpRet.RET_FAILED}
                    else:
                        dict_answer = {'ucRet': KtpRet.RET_OK, 'bApplyNeeded': b_config_modified, 'DiffsToApply': dict_apply_diffs, **dict_config}

                # -- CFG WRITE
                elif msgType == 'ins_cfg_write':
                    ucRet, param_failed = kapri_app.mgr_config_kapri.write_future(msgArg)
                    kapri_app.mgr_audit_logs.audit_log_write(
                        kapri_app.mgr_audit_logs.AUDIT_VIA_INSTRUCTION, user_name=None, ip=None,
                        event=kapri_app.mgr_audit_logs.AUDIT_EVENT_CFG_WRITE, ok=(ucRet == KtpRet.RET_OK)
                    )
                    if ucRet == KtpRet.RET_OK:
                        dict_answer = {'ucRet': KtpRet.RET_OK}
                    else:
                        dict_answer = {'ucRet': ucRet, 'sErrorInParameter': param_failed}

                # -- CFG APPLY
                elif msgType == 'ins_cfg_apply':
                    ucRet = kapri_app.mgr_config_kapri.apply()
                    kapri_app.mgr_audit_logs.audit_log_write(
                        kapri_app.mgr_audit_logs.AUDIT_VIA_INSTRUCTION, user_name=None, ip=None,
                        event=kapri_app.mgr_audit_logs.AUDIT_EVENT_CFG_APPLY, ok=(ucRet == KtpRet.RET_OK)
                    )
                    dict_answer = {'ucRet': ucRet}

                # -- CFG ROLLBACK
                elif msgType == 'ins_cfg_rollback':
                    ucRet = kapri_app.mgr_config_kapri.rollback_apply_diffs()
                    dict_answer = {'ucRet': ucRet}

                # -- CFG BACKUP
                elif msgType == 'ins_cfg_backup':
                    ucRet = kapri_app.mgr_config_kapri.backup_future()
                    kapri_app.mgr_audit_logs.audit_log_write(
                        kapri_app.mgr_audit_logs.AUDIT_VIA_INSTRUCTION, user_name=None, ip=None,
                        event=kapri_app.mgr_audit_logs.AUDIT_EVENT_CFG_BACKUP, ok=(ucRet == KtpRet.RET_OK)
                    )
                    dict_answer = {'ucRet': ucRet}

                # -- CFG RESTORE
                elif msgType == 'ins_cfg_restore':
                    ucRet = kapri_app.mgr_config_kapri.restore_future()
                    kapri_app.mgr_audit_logs.audit_log_write(
                        kapri_app.mgr_audit_logs.AUDIT_VIA_INSTRUCTION, user_name=None, ip=None,
                        event=kapri_app.mgr_audit_logs.AUDIT_EVENT_CFG_RESTORE, ok=(ucRet == KtpRet.RET_OK)
                    )
                    dict_answer = {'ucRet': ucRet}

                # -- CFG FACTORY BACKUP
                elif msgType == 'ins_cfg_factory_backup':
                    ucRet = kapri_app.mgr_config_kapri.backup_factory()
                    kapri_app.mgr_audit_logs.audit_log_write(
                        kapri_app.mgr_audit_logs.AUDIT_VIA_INSTRUCTION, user_name=None, ip=None,
                        event=kapri_app.mgr_audit_logs.AUDIT_EVENT_CFG_FACTORY_BACKUP, ok=(ucRet == KtpRet.RET_OK)
                    )
                    dict_answer = {'ucRet': ucRet}

                # -- CFG FACTORY RESET
                elif msgType == 'ins_cfg_factory_reset':
                    ucRet = kapri_app.mgr_config_kapri.reset_factory()
                    kapri_app.mgr_audit_logs.audit_log_write(
                        kapri_app.mgr_audit_logs.AUDIT_VIA_INSTRUCTION, user_name=None, ip=None,
                        event=kapri_app.mgr_audit_logs.AUDIT_EVENT_CFG_FACTORY_RESET, ok=(ucRet == KtpRet.RET_OK)
                    )
                    dict_answer = {'ucRet': ucRet}

                # #######################################   RTC Real Time Clock    #######
                # -- UTC GET
                elif msgType == 'ins_rtc_dt_utc_get':
                    ucRet, device_dt_utc, local_timezone = kapri_app.mgr_linuxsys.get_dt_utc_timezone()
                    dict_answer = {'ucRet': ucRet, 'device_dt_utc': device_dt_utc}
                # -- UTC SET
                elif msgType == 'ins_rtc_dt_utc_set':
                    try:
                        ucRet = kapri_app.mgr_linuxsys.set_dt_utc(msgArg['device_dt_utc'])
                    except Exception as e:
                        ucRet = KtpRet.RET_INVALIDARGUMENT
                    dict_answer = {'ucRet': ucRet}

                # ####################################   WEB INSTRUCTIONS       #################
                # -- WEB CREDENTIALS SET
                elif msgType == 'ins_web_credentials_set':
                    try:
                        ucRet = kapri_app.mgr_web_users.set_credentials(msgArg['user_name'], msgArg['password_old'], msgArg['password_new'])
                        kapri_app.mgr_audit_logs.audit_log_write(
                            kapri_app.mgr_audit_logs.AUDIT_VIA_INSTRUCTION, user_name=None, ip=None,
                            event=kapri_app.mgr_audit_logs.AUDIT_EVENT_PWD_CHANGE, ok=(ucRet == KtpRet.RET_OK)
                        )
                    except Exception as e:
                        ucRet = KtpRet.RET_INVALIDARGUMENT
                    dict_answer = {'ucRet': ucRet}

                # ####################################   IN/OUT INSTRUCTIONS    #################
                # -- IN-OUT BUZZER OPERATE
                elif msgType == 'ins_inout_buzzer_operate':
                    sEUI64 = None
                    ucMode = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64')  # L' EUI64 de la pròpia Carrier
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    elif msgArg['sPosition'] == 'main_expansion':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    if msgArg['sMode'] == 'off':
                        ucMode = 0
                    elif msgArg['sMode'] == 'on':
                        ucMode = 1
                    elif msgArg['sMode'] == 'beep_30':
                        ucMode = 2
                    elif msgArg['sMode'] == 'beep_50':
                        ucMode = 3
                    elif msgArg['sMode'] == 'beep_70':
                        ucMode = 4
                    if sEUI64 is None or ucMode is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/InOut/BuzzerOperate/0/{ucMode}/{msgArg['ucTime_ds']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --  IN-OUT LED OPERATE
                elif msgType == 'ins_inout_led_operate':
                    sEUI64 = None
                    ucLedNum = 0
                    ucMode = None
                    ucColor = None
                    if msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    elif msgArg['sPosition'] == 'main_expansion':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    if msgArg['sMode'] == 'off':
                        ucMode = 0
                    elif msgArg['sMode'] == 'on':
                        ucMode = 1
                    elif msgArg['sMode'] == 'flash_30':
                        ucMode = 2
                    elif msgArg['sMode'] == 'flash_50':
                        ucMode = 3
                    elif msgArg['sMode'] == 'flash_70':
                        ucMode = 4
                    if msgArg['sColor'] == 'black':
                        ucColor = 0
                    if msgArg['sColor'] == 'red':
                        ucColor = 1
                    if msgArg['sColor'] == 'green':
                        ucColor = 2
                    if msgArg['sColor'] == 'orange':
                        ucColor = 3
                    if msgArg['sColor'] == 'blue':
                        ucColor = 4
                    if msgArg['sColor'] == 'purple':
                        ucColor = 5
                    if msgArg['sColor'] == 'cyan':
                        ucColor = 6
                    if msgArg['sColor'] == 'white':
                        ucColor = 7
                    if sEUI64 is None or ucLedNum is None or ucMode is None or ucColor is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/InOut/LedOperate/{ucLedNum}/{ucMode}/{ucColor}/{msgArg['ucTime_ds']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --IN-OUT LED SWITCH ON
                elif msgType == 'ins_inout_led_switch_on':
                    sEUI64 = None
                    ucLedNum = 0
                    ucMode = None
                    ucColor = None
                    if msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    elif msgArg['sPosition'] == 'main_expansion':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    if msgArg['sMode'] == 'off':
                        ucMode = 0
                    elif msgArg['sMode'] == 'on':
                        ucMode = 1
                    elif msgArg['sMode'] == 'flash_30':
                        ucMode = 2
                    elif msgArg['sMode'] == 'flash_50':
                        ucMode = 3
                    elif msgArg['sMode'] == 'flash_70':
                        ucMode = 4
                    if msgArg['sColor'] == 'black':
                        ucColor = 0
                    if msgArg['sColor'] == 'red':
                        ucColor = 1
                    if msgArg['sColor'] == 'green':
                        ucColor = 2
                    if msgArg['sColor'] == 'orange':
                        ucColor = 3
                    if msgArg['sColor'] == 'blue':
                        ucColor = 4
                    if msgArg['sColor'] == 'purple':
                        ucColor = 5
                    if msgArg['sColor'] == 'cyan':
                        ucColor = 6
                    if msgArg['sColor'] == 'white':
                        ucColor = 7
                    if sEUI64 is None or ucLedNum is None or ucMode is None or ucColor is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/InOut/LedSwitchOn/{ucLedNum}/{ucMode}/{ucColor}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --IN-OUT LED SWITCH OFF
                elif msgType == 'ins_inout_led_switch_off':
                    sEUI64 = None
                    ucLedNum = 0
                    if msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    elif msgArg['sPosition'] == 'main_expansion':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/InOut/LedSwitchOff/{ucLedNum}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
               # --IN-OUT RELAY OPERATE
                elif msgType == 'ins_inout_relay_operate':
                    sEUI64 = None
                    ucMode = 1
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64')    # EL EUI64 de la pròpia Carrier
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    elif msgArg['sPosition'] == 'main_expansion':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/InOut/RelayOperate/{msgArg['ucRelayNum']}/{ucMode}/{msgArg['ucTime_ds']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --IN-OUT RELAY SWITCH ON
                elif msgType == 'ins_inout_relay_switch_on':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64')  # EL EUI64 de la pròpia Carrier
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    elif msgArg['sPosition'] == 'main_expansion':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/InOut/RelaySwitchOn/{msgArg['ucRelayNum']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --IN-OUT RELAY SWITCH OFF
                elif msgType == 'ins_inout_relay_switch_off':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64')  # EL EUI64 de la pròpia Carrier
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    elif msgArg['sPosition'] == 'main_expansion':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/InOut/RelaySwitchOff/{msgArg['ucRelayNum']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --IN-OUT DIGITAL INPUT GET
                elif msgType == 'ins_inout_digital_input_get':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64')  # EL EUI64 de la pròpia Carrier
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    elif msgArg['sPosition'] == 'main_expansion':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/InOut/DigitalInputGet"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            ucDinValue = result.get('ucDinValue')
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                            bDinList = []
                            bDinList.append( (ucDinValue & 0x01) != 0 )
                            bDinList.append( (ucDinValue & 0x02) != 0 )
                            if msgArg['sPosition'] == 'main':
                                bDinList.append( (ucDinValue & 0x04) != 0 )
                                bDinList.append( (ucDinValue & 0x08) != 0 )
                                bDinList.append( (ucDinValue & 0x10) != 0 )
                            dict_answer['bDinValueList'] = bDinList

                # ####################################   MIFARE INSTRUCTIONS    #################
                # -- MIFARE ATQA-UID GET
                elif msgType == 'ins_mifare_atqa_uid_get':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/ATQA_UID_Get"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'sATQA': result.get('sATQA'),
                                'ucCardType': result.get('ucCardType'),
                                'ucSAK': result.get('ucSAK'),
                                'sData': result.get('sData')
                            }
                # --MIFARE HALT
                elif msgType == 'ins_mifare_halt':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/Halt"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --MIFARE WAKE-UP
                elif msgType == 'ins_mifare_wakeup':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/WakeUp"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'ucErrCode': result.get('ucErrCode'),
                                'sATQA': result.get('sATQA')
                            }
                # --MIFARE LOGIN
                elif msgType == 'ins_mifare_login':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/Login/{msgArg['ucBlockNumber']}/{msgArg['sKeyAB']}/{msgArg['sKey']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --MIFARE BLOCK READ
                elif msgType == 'ins_mifare_block_read':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/BlockRead/{msgArg['ucBlockNumber']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'sData': result.get('sData')
                            }
                # --MIFARE BLOCK WRITE
                elif msgType == 'ins_mifare_block_write':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/BlockWrite/{msgArg['ucBlockNumber']}/{msgArg['sData']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --MIFARE BLOCK BACKUP
                elif msgType == 'ins_mifare_block_backup':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/BlockBackUp/{msgArg['ucBlockNumberFrom']}/{msgArg['ucBlockNumberTo']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --MIFARE SECTOR READ
                elif msgType == 'ins_mifare_sector_read':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/SectorRead/{msgArg['ucBlockNumber']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'sData': result.get('sData')
                            }
                # --MIFARE SECTOR WRITE
                elif msgType == 'ins_mifare_sector_write':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/SectorWrite/{msgArg['ucBlockNumber']}/{msgArg['sData']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --MIFARE VALUE READ
                elif msgType == 'ins_mifare_value_read':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/ValueRead/{msgArg['ucBlockNumber']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'i32Value': result.get('i32Value'),
                                'ucAddress': result.get('ucAddress')
                            }
                # --MIFARE VALUE WRITE
                elif msgType == 'ins_mifare_value_write':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/ValueWrite/{msgArg['ucBlockNumber']}/{msgArg['i32Value']}/{msgArg['ucAddress']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --MIFARE VALUE INCREMENT
                elif msgType == 'ins_mifare_value_increment':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/ValueIncrement/{msgArg['ucBlockNumber']}/{msgArg['i32Delta']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --MIFARE VALUE DECREMENT
                elif msgType == 'ins_mifare_value_decrement':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/ValueDecrement/{msgArg['ucBlockNumber']}/{msgArg['i32Delta']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --MIFARE VALUE RESTORE
                elif msgType == 'ins_mifare_value_restore':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/ValueRestore/{msgArg['ucBlockNumberFrom']}/{msgArg['ucBlockNumberTo']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}
                # --MIFARE SECURITY LEVEL READ
                elif msgType == 'ins_mifare_security_level_read':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/SecurityLevelRead"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'ucSecurityLevel': result.get('ucSecurityLevel')
                            }
                # --MIFARE SECURITY LEVEL WRITE
                elif msgType == 'ins_mifare_security_level_write':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/SecurityLevelWrite/{msgArg['ucSecurityLevel']}/{msgArg['ucKeyNumber']}/{msgArg['sKey']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'ucRetryCounter': result.get('ucRetryCounter')
                            }
                # --MIFARE KEY WRITE
                elif msgType == 'ins_mifare_key_write':
                    sEUI64 = None
                    if msgArg['sPosition'] == 'main':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaMain')
                    elif msgArg['sPosition'] == 'aux':
                        sEUI64 = kapri_app.mgr_hardware_info.get('sEUI64_LexaAux')
                    # construim instrucció
                    if sEUI64 is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{sEUI64}/Mifare/KeyWrite/{msgArg['ucKeyNumber']}/{msgArg['sKey']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}

                # ####################################   FIM INSTRUCTIONS    #################
                # -- FIM GET DEVICE INFO
                elif msgType == 'ins_fim_get_device_info':
                    ucFimNum = None
                    if msgArg['sPosition'] == 'main':
                        ucFimNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucFimNum = 1
                    # construim instrucció
                    if ucFimNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Fim/GetDeviceInfo/{ucFimNum}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'uiFimParam1': result.get('uiFimParam1'),
                                'uiFimParam2': result.get('uiFimParam2')
                            }
                # -- FIM GET FIRMWARE VERSION
                elif msgType == 'ins_fim_get_firmware_version':
                    ucFimNum = None
                    if msgArg['sPosition'] == 'main':
                        ucFimNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucFimNum = 1
                    # construim instrucció
                    if ucFimNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Fim/GetFirmwareVersion/{ucFimNum}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'uiFimParam1': result.get('uiFimParam1'),
                                'uiFimParam2': result.get('uiFimParam2')
                            }
                # -- FIM GET TEMPLATE
                elif msgType == 'ins_fim_get_template':
                    ucFimNum = None
                    if msgArg['sPosition'] == 'main':
                        ucFimNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucFimNum = 1
                    # construim instrucció
                    if ucFimNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Fim/GetTemplate/{ucFimNum}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'uiFimParam1': result.get('uiFimParam1'),
                                'sFimTemplate': result.get('sFimTemplate')
                            }
                # -- FIM INSTANT MATCHING
                # -- POST METHOD
                elif msgType == 'ins_fim_instant_matching':
                    ucFimNum = None
                    if msgArg['sPosition'] == 'main':
                        ucFimNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucFimNum = 1
                    # construim instrucció
                    if ucFimNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Fim/InstantMatching/{ucFimNum}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        dictio = msgArg
                        result = PostWoman.send_post(my_url, dictio)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'uiFimParam1': result.get('uiFimParam1')
                            }
                # -- FIM ENTER MASTER MODE
                elif msgType == 'ins_fim_enter_master_mode':
                    ucFimNum = None
                    if msgArg['sPosition'] == 'main':
                        ucFimNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucFimNum = 1
                    # construim instrucció
                    if ucFimNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Fim/EnterMasterMode/{ucFimNum}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'uiFimParam1': result.get('uiFimParam1')
                            }
                # -- FIM LEAVE MASTER MODE
                elif msgType == 'ins_fim_leave_master_mode':
                    ucFimNum = None
                    if msgArg['sPosition'] == 'main':
                        ucFimNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucFimNum = 1
                    # construim instrucció
                    if ucFimNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Fim/LeaveMasterMode/{ucFimNum}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'uiFimParam1': result.get('uiFimParam1')
                            }
                # -- FIM GET NUMBER OF USERS
                elif msgType == 'ins_fim_get_number_of_users':
                    ucFimNum = None
                    if msgArg['sPosition'] == 'main':
                        ucFimNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucFimNum = 1
                    # construim instrucció
                    if ucFimNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Fim/GetNumberOfUsers/{ucFimNum}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'uiFimParam1': result.get('uiFimParam1'),
                                'uiFimNumberOfUsers': result.get('uiFimNumberOfUsers')
                            }
                # -- FIM DELETE USER
                elif msgType == 'ins_fim_delete_user':
                    ucFimNum = None
                    if msgArg['sPosition'] == 'main':
                        ucFimNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucFimNum = 1
                    # construim instrucció
                    if ucFimNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Fim/DeleteUser/{ucFimNum}/{msgArg['sFimUserIdent']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'uiFimParam1': result.get('uiFimParam1'),
                                'uiFimParam2': result.get('uiFimParam2')
                            }
                # -- FIM DELETE ALL USERS
                elif msgType == 'ins_fim_delete_all_users':
                    ucFimNum = None
                    if msgArg['sPosition'] == 'main':
                        ucFimNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucFimNum = 1
                    # construim instrucció
                    if ucFimNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Fim/DeleteAllUsers/{ucFimNum}/{msgArg['sFimIncludeMaster']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'uiFimParam1': result.get('uiFimParam1')
                            }
                # -- FIM ADD USER
                # -- POST METHOD
                elif msgType == 'ins_fim_add_user':
                    ucFimNum = None
                    if msgArg['sPosition'] == 'main':
                        ucFimNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucFimNum = 1
                    # construim instrucció
                    if ucFimNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Fim/AddUser/{ucFimNum}/{msgArg['sFimUserIdent']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        dictio = msgArg
                        result = PostWoman.send_post(my_url, dictio)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'uiFimParam1': result.get('uiFimParam1')
                            }
                # -- FIM IDENTIFY USER
                elif msgType == 'ins_fim_identify_user':
                    ucFimNum = None
                    if msgArg['sPosition'] == 'main':
                        ucFimNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucFimNum = 1
                    # construim instrucció
                    if ucFimNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Fim/IdentifyUser/{ucFimNum}"
                        if msgArg.get('sFimUserIdent') is not None:
                            params += f"/{msgArg['sFimUserIdent']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'uiFimParam1': result.get('uiFimParam1'),
                                'sFimUserIdent': result.get('sFimUserIdent'),
                                'ucFimTemplateIdx': result.get('ucFimTemplateIdx')
                            }
                # -- FIM VERIFY USER
                # -- POST METHOD
                elif msgType == 'ins_fim_verify_user':
                    ucFimNum = None
                    if msgArg['sPosition'] == 'main':
                        ucFimNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucFimNum = 1
                    # construim instrucció
                    if ucFimNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Fim/VerifyUser/{ucFimNum}/{msgArg['sFimUserIdent']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        dictio = msgArg
                        result = PostWoman.send_post(my_url, dictio)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'uiFimParam1': result.get('uiFimParam1'),
                                'uiFimParam2': result.get('uiFimParam2')
                            }
                # -- FIM TRANSCEIVE
                # -- POST METHOD
                elif msgType == 'ins_fim_transceive':
                    ucFimNum = None
                    if msgArg['sPosition'] == 'main':
                        ucFimNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucFimNum = 1
                    # construim instrucció
                    if ucFimNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Fim/Transceive/{ucFimNum}/{msgArg['uiFimCommand']}/{msgArg['uiFimParam1']}/{msgArg['uiFimParam2']}/{msgArg['uiFimErrorCode']}/{msgArg['uiRxExpectedDataSize']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        dictio = msgArg
                        result = PostWoman.send_post(my_url, dictio)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'uiFimCommand': result.get('uiFimCommand'),
                                'uiFimParam1': result.get('uiFimParam1'),
                                'uiFimParam2': result.get('uiFimParam2'),
                                'uiFimDataSize': result.get('uiFimDataSize'),
                                'uiFimErrorCode': result.get('uiFimErrorCode'),
                                'baFimData': result.get('baFimData')
                            }

                # ####################################   SFM INSTRUCTIONS    #################
                # -- SFM GET DEVICE INFO
                elif msgType == 'ins_sfm_get_device_info':
                    ucSfmNum = None
                    if msgArg['sPosition'] == 'main':
                        ucSfmNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucSfmNum = 1
                    # construim instrucció
                    if ucSfmNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Sfm/GetDeviceInfo/{ucSfmNum}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'ucInfo': result.get('ucInfo')
                            }
                # -- SFM GET FIRMWARE VERSION
                elif msgType == 'ins_sfm_get_firmware_version':
                    ucSfmNum = None
                    if msgArg['sPosition'] == 'main':
                        ucSfmNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucSfmNum = 1
                    # construim instrucció
                    if ucSfmNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Sfm/GetFirmwareVersion/{ucSfmNum}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'sFwVer': result.get('sFwVer')
                            }
                # -- SFM GET TEMPLATE
                elif msgType == 'ins_sfm_get_template':
                    ucSfmNum = None
                    if msgArg['sPosition'] == 'main':
                        ucSfmNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucSfmNum = 1
                    # construim instrucció
                    if ucSfmNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Sfm/GetTemplate/{ucSfmNum}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'ucSfmResult': result.get('ucSfmResult'),
                                'ucSfmQuality': result.get('ucSfmQuality'),
                                'baSfmTemplate': result.get('baSfmTemplate')
                            }
                # -- SFM INSTANT MATCHING
                # -- POST METHOD
                elif msgType == 'ins_sfm_instant_matching':
                    ucSfmNum = None
                    if msgArg['sPosition'] == 'main':
                        ucSfmNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucSfmNum = 1
                    # construim instrucció
                    if ucSfmNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Sfm/InstantMatching/{ucSfmNum}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        dictio = msgArg
                        result = PostWoman.send_post(my_url, dictio)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'ucSfmResult': result.get('ucSfmResult')
                            }
                # -- SFM GET NUMBER OF TEMPLATES
                elif msgType == 'ins_sfm_get_number_of_templates':
                    ucSfmNum = None
                    if msgArg['sPosition'] == 'main':
                        ucSfmNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucSfmNum = 1
                    # construim instrucció
                    if ucSfmNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Sfm/GetNumberOfTemplates/{ucSfmNum}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'uiSfmNumberOfTemplates': result.get('uiSfmNumberOfTemplates')
                            }
                # -- SFM DELETE USER
                elif msgType == 'ins_sfm_delete_user':
                    ucSfmNum = None
                    if msgArg['sPosition'] == 'main':
                        ucSfmNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucSfmNum = 1
                    # construim instrucció
                    if ucSfmNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Sfm/DeleteUser/{ucSfmNum}/{msgArg['uiUserId']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'ucSfmResult': result.get('ucSfmResult')
                            }
                # -- SFM DELETE ALL USERS
                elif msgType == 'ins_sfm_delete_all_users':
                    ucSfmNum = None
                    if msgArg['sPosition'] == 'main':
                        ucSfmNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucSfmNum = 1
                    # construim instrucció
                    if ucSfmNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Sfm/DeleteAllUsers/{ucSfmNum}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'ucSfmResult': result.get('ucSfmResult')
                            }
                # -- SFM ADD USER
                # -- POST METHOD
                elif msgType == 'ins_sfm_add_user':
                    ucSfmNum = None
                    if msgArg['sPosition'] == 'main':
                        ucSfmNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucSfmNum = 1
                    # construim instrucció
                    if ucSfmNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Sfm/AddUser/{ucSfmNum}/{msgArg['uiUserId']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        dictio = msgArg
                        result = PostWoman.send_post(my_url, dictio)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'ucSfmResult': result.get('ucSfmResult'),
                                'ucNumFeatures': result.get('ucNumFeatures')
                            }
                # -- SFM IDENTIFY USER
                elif msgType == 'ins_sfm_identify_user':
                    ucSfmNum = None
                    if msgArg['sPosition'] == 'main':
                        ucSfmNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucSfmNum = 1
                    # construim instrucció
                    if ucSfmNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Sfm/IdentifyUser/{ucSfmNum}"
                        if msgArg.get('uiUserId') is not None:
                            params += f"/{msgArg['uiUserId']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        result = PostWoman.send_get(my_url)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'ucSfmResult': result.get('ucSfmResult'),
                                'uiUserId': result.get('uiUserId'),
                                'uiSubId': result.get('uiSubId')
                            }
                # -- SFM VERIFY USER
                # -- POST METHOD
                elif msgType == 'ins_sfm_verify_user':
                    ucSfmNum = None
                    if msgArg['sPosition'] == 'main':
                        ucSfmNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucSfmNum = 1
                    # construim instrucció
                    if ucSfmNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Sfm/VerifyUser/{ucSfmNum}/{msgArg['uiUserId']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        dictio = msgArg
                        result = PostWoman.send_post(my_url, dictio)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'ucSfmResult': result.get('ucSfmResult'),
                                'uiSubId': result.get('uiSubId')
                            }
                # -- SFM TRANSCEIVE
                # -- POST METHOD
                elif msgType == 'ins_sfm_transceive':
                    ucSfmNum = None
                    if msgArg['sPosition'] == 'main':
                        ucSfmNum = 0
                    elif msgArg['sPosition'] == 'aux':
                        ucSfmNum = 1
                    # construim instrucció
                    if ucSfmNum is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Sfm/Transceive/{ucSfmNum}/{msgArg['ucSfmCommand']}/{msgArg['uiSfmParam']}/{msgArg['uiSfmSize']}/{msgArg['ucSfmFlagError']}/{msgArg['uiRxExpectedDataSize']}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        dictio = msgArg
                        result = PostWoman.send_post(my_url, dictio)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {
                                'ucRet': KtpRet.RET_OK,
                                'ucSfmCommand': result.get('ucSfmCommand'),
                                'uiSfmParam': result.get('uiSfmParam'),
                                'uiSfmSize': result.get('uiSfmSize'),
                                'ucSfmFlagError': result.get('ucSfmFlagError'),
                                'baSfmData': result.get('baSfmData')
                            }

                # ####################################   UART INSTRUCTIONS    #################
                # -- UART SEND
                # -- POST METHOD
                elif msgType == 'ins_uart_send':
                    ucUartNumber = None
                    if msgArg['sPosition'] == 'main':
                        ucUartNumber = 1
                    elif msgArg['sPosition'] == 'aux':
                        ucUartNumber = 2
                    # construim instrucció
                    if ucUartNumber is None:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                    else:
                        params = f"/api/nodes/{kapri_app.mgr_hardware_info.get('sEUI64')}/Uart/Send/{ucUartNumber}"
                        my_url = kapri_app.app.config['URL']['url_kxphostproapi'] + params
                        dictio = msgArg
                        result = PostWoman.send_post(my_url, dictio)
                        if result.get('ucInsRet') == 0:
                            dict_answer = {'ucRet': KtpRet.RET_OK}

                # ####################################   KYBMGR INSTRUCTIONS    #################
                # -- PAUSE
                elif msgType == 'ins_kybmgr_pause':
                    kapri_app.mgr_kybmgr.pause()
                    dict_answer = {'ucRet': KtpRet.RET_OK}
                # --RESUME
                elif msgType == 'ins_kybmgr_resume':
                    kapri_app.mgr_kybmgr.resume()
                    dict_answer = {'ucRet': KtpRet.RET_OK}

                # ####################################   LBLMGR INSTRUCTIONS    #################
                # -- GET
                elif msgType == 'ins_lblmgr_get':
                    data = kapri_app.mgr_lblmgr.get_data()
                    dict_answer = {'ucRet': KtpRet.RET_OK, 'oData': data}
                # --SET
                elif msgType == 'ins_lblmgr_set':
                    data = msgArg['oData']
                    b_ok = kapri_app.mgr_lblmgr.set_data(data)
                    if b_ok:
                        dict_answer = {'ucRet': KtpRet.RET_OK}
                    else:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                # --CLEAR
                elif msgType == 'ins_lblmgr_clear':
                    kapri_app.mgr_lblmgr.clear_data()
                    dict_answer = {'ucRet': KtpRet.RET_OK}

                # ####################################   USRTIMER INSTRUCTIONS    #################
                # --SET
                elif msgType == 'ins_usrtimer_set':
                    try:
                        arg_val = msgArg['uiTime']
                        uc_time_sec = KCheck.integerInInterval(arg_val, 1, 300)
                    except Exception as e:
                        uc_time_sec = None
                    if uc_time_sec is not None:
                        kapri_app.mgr_usrtimer.set_tmo(uc_time_sec)
                        dict_answer = {'ucRet': KtpRet.RET_OK}
                    else:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                # --CLEAR
                elif msgType == 'ins_usrtimer_clear':
                    kapri_app.mgr_usrtimer.clear_tmo()
                    dict_answer = {'ucRet': KtpRet.RET_OK}

                # ####################################   SCREEN HTML INSTRUCTIONS    #################
                # -- DOCUMENT.WRITE
                elif msgType == 'ins_screen_html_document_write':
                    sHtml = msgArg.get('sHtml')
                    if HtmlCheck.check(sHtml):
                        kapri_app.mgr_guispy.write_screen_html(msgArg.get('sHtml'))
                        dict_answer = {'ucRet': KtpRet.RET_OK}
                    else:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}

                # #######################################   SCREEN IMAGE    #####################
                # --STORE
                elif msgType == 'ins_screen_image_store':
                    try:
                        ucRet = kapri_app.mgr_images.store(msgArg['sImgName'], msgArg['sImgB64'])
                    except Exception as e:
                        ucRet = KtpRet.RET_INVALIDARGUMENT
                    dict_answer = {'ucRet': ucRet}
                # --RETRIEVE
                elif msgType == 'ins_screen_image_retrieve':
                    ucRet, sImgB64 = kapri_app.mgr_images.retrieve(msgArg['sImgName'])
                    dict_answer = {'ucRet': ucRet}
                    if ucRet == KtpRet.RET_OK:
                        dict_answer['sImgB64'] = sImgB64
                # --LIST
                elif msgType == 'ins_screen_image_list':
                    ucRet, listImgNames = kapri_app.mgr_images.list()
                    dict_answer = {'ucRet': ucRet}
                    if ucRet == KtpRet.RET_OK:
                        dict_answer['listImgNames'] = listImgNames
                # --REMOVE
                elif msgType == 'ins_screen_image_remove':
                    try:
                        ucRet = kapri_app.mgr_images.remove(msgArg['sImgName'])
                    except Exception as e:
                        ucRet = KtpRet.RET_INVALIDARGUMENT
                    dict_answer = {'ucRet': ucRet}

                # #######################################   CLOUD    #####################
                # --SLEEP
                elif msgType == 'ins_cloud_sleep':
                    uc_time_sec = None
                    try:
                        arg_val = msgArg['ufTime']
                        uc_time_sec = KCheck.floatInInterval(arg_val, 0.0, 20.0)
                    except Exception as e:
                        try:
                            arg_val = msgArg['ucTime_10ms']
                            uc_time_10ms = KCheck.integerInInterval(arg_val, 0, 255)
                            uc_time_sec = uc_time_10ms / 100
                        except Exception as e:
                            uc_time_sec = None
                    if uc_time_sec is not None:
                        time.sleep(uc_time_sec)
                        dict_answer = {'ucRet': KtpRet.RET_OK}
                    else:
                        dict_answer = {'ucRet': KtpRet.RET_INVALIDARGUMENT}
                ### SEMI-OFFLINE
                elif msgType == 'ins_cloud_semi_offline':
                    event = msgArg['event']
                    kapri_app.mgr_semi_offline.manage_event(event)
                    dict_answer = {'ucRet': KtpRet.RET_OK}

                # #######################################   EVENTS SEMI OFFLINE    #####################
                # --GET RANGE
                elif msgType == 'ins_semi_offline_events_get_range':
                    ucRet, semi_offline_events_list = kapri_app.mgr_semi_offline_events.get_range(msgArg.get('from_dt_utc'), msgArg.get('to_dt_utc'))
                    dict_answer = {'ucRet': ucRet, 'semi_offline_events_list': semi_offline_events_list}
                # --DELETE RANGE
                elif msgType == 'ins_semi_offline_events_delete_range':
                    try:
                        ucRet = kapri_app.mgr_semi_offline_events.delete_range(msgArg.get('from_dt_utc'), msgArg['to_dt_utc'])
                    except Exception as e:
                        ucRet = KtpRet.RET_INVALIDARGUMENT
                    dict_answer = {'ucRet': ucRet}

                # #######################################  SEMI OFFLINE LISTS (WHITE/BLACK) ###############
                # --WHITE LIST GET ALL
                elif msgType == 'ins_semi_offline_white_list_get':
                    ucRet, semi_offline_list_of_codes = kapri_app.mgr_semi_offline_lists.get_white(msgArg)
                    dict_answer = {'ucRet': ucRet, 'semi_offline_list_of_codes': semi_offline_list_of_codes}
                # --BLACK LIST GET ALL
                elif msgType == 'ins_semi_offline_black_list_get':
                    ucRet, semi_offline_list_of_codes = kapri_app.mgr_semi_offline_lists.get_black(msgArg)
                    dict_answer = {'ucRet': ucRet, 'semi_offline_list_of_codes': semi_offline_list_of_codes}
                # --WHITE LIST SET ALL
                elif msgType == 'ins_semi_offline_white_list_set':
                    try:
                        ucRet = kapri_app.mgr_semi_offline_lists.set_white(msgArg['semi_offline_list_of_codes'])
                    except Exception as e:
                        ucRet = KtpRet.RET_INVALIDARGUMENT
                    dict_answer = {'ucRet': ucRet}
                # --BLACK LIST SET ALL
                elif msgType == 'ins_semi_offline_black_list_set':
                    try:
                        ucRet = kapri_app.mgr_semi_offline_lists.set_black(msgArg['semi_offline_list_of_codes'])
                    except Exception as e:
                        ucRet = KtpRet.RET_INVALIDARGUMENT
                    dict_answer = {'ucRet': ucRet}
                # --WHITE APPEND
                elif msgType == 'ins_semi_offline_white_list_append':
                    try:
                        ucRet = kapri_app.mgr_semi_offline_lists.append_white(msgArg['semi_offline_list_of_codes'])
                    except Exception as e:
                        ucRet = KtpRet.RET_INVALIDARGUMENT
                    dict_answer = {'ucRet': ucRet}
                # --BLACK APPEND
                elif msgType == 'ins_semi_offline_black_list_append':
                    try:
                        ucRet = kapri_app.mgr_semi_offline_lists.append_black(msgArg['semi_offline_list_of_codes'])
                    except Exception as e:
                        ucRet = KtpRet.RET_INVALIDARGUMENT
                    dict_answer = {'ucRet': ucRet}
                # --WHITE REMOVE
                elif msgType == 'ins_semi_offline_white_list_remove':
                    try:
                        ucRet = kapri_app.mgr_semi_offline_lists.remove_white(msgArg['semi_offline_list_of_codes'])
                    except Exception as e:
                        ucRet = KtpRet.RET_INVALIDARGUMENT
                    dict_answer = {'ucRet': ucRet}
                # --BLACK REMOVE
                elif msgType == 'ins_semi_offline_black_list_remove':
                    try:
                        ucRet = kapri_app.mgr_semi_offline_lists.remove_black(msgArg['semi_offline_list_of_codes'])
                    except Exception as e:
                        ucRet = KtpRet.RET_INVALIDARGUMENT
                    dict_answer = {'ucRet': ucRet}

                # #######################################  OPTSEL ###############
                # RUN
                elif msgType == 'ins_optsel_run':
                    try:
                        ucRet = kapri_app.mgr_optsel.run(msgArg)
                    except Exception as e:
                        ucRet = KtpRet.RET_INVALIDARGUMENT
                    dict_answer = {'ucRet': ucRet}

                # --ALTRES TYPES
                else:
                    dict_answer = {'ucRet': KtpRet.RET_INVALIDTYPE}

            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
                dict_answer = {'ucRet': KtpRet.RET_EXCEPTION}
            return 'OK', dict_answer
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return 'Error: '+ str(e), None
