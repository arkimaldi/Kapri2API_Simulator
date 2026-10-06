# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.


class ConfigTranslator:
    # #############################################  BLOC KAPRI (CARRIER) #############################################
    # PROCEDIMENTS PUBLICS
    """
    pren un diccionari amb k:v on
        k: es el nom del paràmetre de configuració d'alt nivell de la carrier del Kapri
        v: es el valor d'alt nivell que pren el paràmetre

    retorna:
        tres diccionaris f1, f2 i f3 per cada configuració de la carrier del kapri on:
        k: es el número de paràmetre
        v: es el valor en format ascii-hex
        de forma que els items de dict_params queden traduits en hexa a la posició corresponent,
        i els que no s'especifiquin a dict_params es retornaràn com None
    """

    @staticmethod
    def kapri_translate_to_low_level(dict_params):
        # inicialitzem valors de retorn
        d_f1 = {}
        d_f2 = {}
        d_f3 = {}
        for idx in range(0, 1 + 0x3f):
            d_f1[idx] = None
            d_f2[idx] = None
            d_f3[idx] = None

        # F1
        # 0x00 a 0x0f RESERVAT
        # 0x10 - CFG1_PAR_KXP_ADDR_H (NO MODIFICAR)
        # 0x11 - CFG1_PAR_KXP_ADDR_L (NO MODIFICAR)
        # 0x12 - # CFG1_PAR_SCI0_BAUD (NO MODIFICAR)
        # 0x13 - CFG1_PAR_SCI1_BAUD
        d_f1[0x13] = ConfigTranslator.translate_scibaud_to_low_level(dict_params.get('cfg_sci1_baud'))
        # 0x14 - CFG1_PAR_SCI2_BAUD
        d_f1[0x14] = ConfigTranslator.translate_scibaud_to_low_level(dict_params.get('cfg_sci2_baud'))
        # 0x15 a 0x3f RESERVAT

        # F2
        # 0x00 a 0x3f RESERVAT

        # F3
        # 0x00 - RESERVAT
        # 0x01 - CFG3_PAR_HOST_FE (NO MODIFICAR)
        # 0x02 - CFG3_PAR_UART0_MODE (NO MODIFICAR)
        # 0x03 - CFG3_PAR_UART1_MODE
        d_f3[0x03] = ConfigTranslator.translate_sci1mode_to_low_level(dict_params.get('cfg_sci1_mode'))
        # 0x04 - CFG3_PAR_UART2_MODE
        d_f3[0x04] = ConfigTranslator.translate_sci2mode_to_low_level(dict_params.get('cfg_sci2_mode'))
        # 0x05 - RESERVAT
        # 0x06 - CFG3_PAR_DIN_ECHO
        d_f3[0x06] = ConfigTranslator.translate_dinecho01234_to_low_level(dict_params.get('cfg_din_echo_0'),
                                                                          dict_params.get('cfg_din_echo_1'),
                                                                          dict_params.get('cfg_din_echo_2'),
                                                                          dict_params.get('cfg_din_echo_3'),
                                                                          dict_params.get('cfg_din_echo_4'))
        # 0x07 - RESERVAT
        # 0x08 - CFG3_PAR_TTL0_MODE
        d_f3[0x08] = ConfigTranslator.translate_ttlmode_to_low_level(dict_params.get('cfg_ttl0_mode'))
        # 0x09 - CFG3_PAR_TTL1_MODE
        d_f3[0x09] = ConfigTranslator.translate_ttlmode_to_low_level(dict_params.get('cfg_ttl1_mode'))
        # 0x0a - RESERVAT
        # 0x0b - CFG3_PAR_FIM0_OPERATING_BAUD_R
        d_f3[0x0b] = ConfigTranslator.translate_fimoperatingbaud_to_low_level(dict_params.get('cfg_fim0_operating_baud'))
        # 0x0c - CFG3_PAR_FIM1_OPERATING_BAUD_R
        d_f3[0x0c] = ConfigTranslator.translate_fimoperatingbaud_to_low_level(dict_params.get('cfg_fim1_operating_baud'))
        # 0x0d - CFG3_PAR_SFM0_OPERATING_BAUD_R
        d_f3[0x0d] = ConfigTranslator.translate_sfmoperatingbaud_to_low_level(dict_params.get('cfg_sfm0_operating_baud'))
        # 0x0e - CFG3_PAR_SFM1_OPERATING_BAUD_R
        d_f3[0x0e] = ConfigTranslator.translate_sfmoperatingbaud_to_low_level(dict_params.get('cfg_sfm1_operating_baud'))
        # 0x0f a 0x3f RESERVAT

        return d_f1, d_f2, d_f3



    """"
    pren tres strings hex ascii,
        un per cada cfg 1,2,3
    retorna:
        un diccionari amb k:v on
            k: es el nom del paràmetre de configuració d'alt nivell de la carrier del Kapri
            v: es el valor d'alt nivell que pren el paràmetre
    """

    @staticmethod
    def kapri_translate_to_high_level(s_f1, s_f2, s_f3):
        # inicialitzem valors de retorn
        dict_params = {}

        try:
            d_f1 = {}
            d_f2 = {}
            d_f3 = {}
            for idx in range(0, 1 + 0x3f):
                d_f1[idx] = s_f1[2*idx:2*idx+2].lower()
                d_f2[idx] = s_f2[2*idx:2*idx+2].lower()
                d_f3[idx] = s_f3[2*idx:2*idx+2].lower()
        except Exception as e:
            return dict_params

        # F1
        # 0x00 a 0x0f RESERVAT
        # 0x10 - CFG1_PAR_KXP_ADDR_H (NO MODIFICAR)
        # 0x11 - CFG1_PAR_KXP_ADDR_L (NO MODIFICAR)
        # 0x12 - # CFG1_PAR_SCI0_BAUD (NO MODIFICAR)
        # 0x13 - CFG1_PAR_SCI1_BAUD
        tmp = ConfigTranslator.translate_scibaud_to_high_level(d_f1[0x13])
        if tmp is not None:
            dict_params['cfg_sci1_baud'] = tmp
        # 0x14 - CFG1_PAR_SCI2_BAUD
        tmp = ConfigTranslator.translate_scibaud_to_high_level(d_f1[0x14])
        if tmp is not None:
            dict_params['cfg_sci2_baud'] = tmp
        # 0x15 a 0x3f RESERVAT

        # F2
        # 0x00 a 0x3f RESERVAT

        # F3
        # 0x00 - RESERVAT
        # 0x01 - CFG3_PAR_HOST_FE (NO MODIFICAR)
        # 0x02 - CFG3_PAR_UART0_MODE (NO MODIFICAR)
        # 0x03 - CFG3_PAR_UART1_MODE
        tmp = ConfigTranslator.translate_sci1mode_to_high_level(d_f3[0x03])
        if tmp is not None:
            dict_params['cfg_sci1_mode'] = tmp
        # 0x04 - CFG3_PAR_UART2_MODE
        tmp = ConfigTranslator.translate_sci2mode_to_high_level(d_f3[0x04])
        if tmp is not None:
            dict_params['cfg_sci2_mode'] = tmp
        # 0x05 - RESERVAT
        # 0x06 - CFG3_PAR_DIN_ECHO
        tmp_0, tmp_1, tmp_2, tmp_3, tmp_4 = ConfigTranslator.translate_dinecho01234_to_high_level(d_f3[0x06])
        if tmp_0 is not None:
            dict_params['cfg_din_echo_0'] = tmp_0
        if tmp_1 is not None:
            dict_params['cfg_din_echo_1'] = tmp_1
        if tmp_2 is not None:
            dict_params['cfg_din_echo_2'] = tmp_2
        if tmp_3 is not None:
            dict_params['cfg_din_echo_3'] = tmp_3
        if tmp_4 is not None:
            dict_params['cfg_din_echo_4'] = tmp_4

        # 0x07 - RESERVAT
        # 0x08 - CFG3_PAR_TTL0_MODE
        tmp = ConfigTranslator.translate_ttlmode_to_high_level(d_f3[0x08])
        if tmp is not None:
            dict_params['cfg_ttl0_mode'] = tmp
        # 0x09 - CFG3_PAR_TTL1_MODE
        tmp = ConfigTranslator.translate_ttlmode_to_high_level(d_f3[0x09])
        if tmp is not None:
            dict_params['cfg_ttl1_mode'] = tmp
        # 0x0a - RESERVAT
        # 0x0b - CFG3_PAR_FIM0_OPERATING_BAUD_R
        tmp = ConfigTranslator.translate_fimoperatingbaud_to_high_level(d_f3[0x0b])
        if tmp is not None:
            dict_params['cfg_fim0_operating_baud'] = tmp
        # 0x0c - CFG3_PAR_FIM1_OPERATING_BAUD_R
        tmp = ConfigTranslator.translate_fimoperatingbaud_to_high_level(d_f3[0x0c])
        if tmp is not None:
            dict_params['cfg_fim1_operating_baud'] = tmp
        # 0x0d - CFG3_PAR_SFM0_OPERATING_BAUD_R
        tmp = ConfigTranslator.translate_sfmoperatingbaud_to_high_level(d_f3[0x0d])
        if tmp is not None:
            dict_params['cfg_sfm0_operating_baud'] = tmp
        # 0x0e - CFG3_PAR_SFM1_OPERATING_BAUD_R
        tmp = ConfigTranslator.translate_sfmoperatingbaud_to_high_level(d_f3[0x0e])
        if tmp is not None:
            dict_params['cfg_sfm1_operating_baud'] = tmp
        # 0x0f a 0x3f RESERVAT

        return dict_params

    # ##############################################################
    # mètodes interns PRIVATS. No fer servir des de fora de la classe
    # ##############################################################

    # scibaud: cfg_sci_baud i CFG1_PAR_SCIx_BAUD
    @staticmethod
    def translate_scibaud_to_low_level(i_cfg_sci_baud):
        CFG1_PAR_SCIx_BAUD = None
        if i_cfg_sci_baud == 1200:
            CFG1_PAR_SCIx_BAUD = '00'
        elif i_cfg_sci_baud == 2400:
            CFG1_PAR_SCIx_BAUD = '01'
        elif i_cfg_sci_baud == 4800:
            CFG1_PAR_SCIx_BAUD = '02'
        elif i_cfg_sci_baud == 9600:
            CFG1_PAR_SCIx_BAUD = '03'
        elif i_cfg_sci_baud == 19200:
            CFG1_PAR_SCIx_BAUD = '04'
        elif i_cfg_sci_baud == 38400:
            CFG1_PAR_SCIx_BAUD = '05'
        elif i_cfg_sci_baud == 57600:
            CFG1_PAR_SCIx_BAUD = '06'
        elif i_cfg_sci_baud == 115200:
            CFG1_PAR_SCIx_BAUD = '07'
        return CFG1_PAR_SCIx_BAUD

    @staticmethod
    def translate_scibaud_to_high_level(CFG1_PAR_SCIx_BAUD):
        i_cfg_sci_baud = None
        if CFG1_PAR_SCIx_BAUD == '00':
            i_cfg_sci_baud = 1200
        elif CFG1_PAR_SCIx_BAUD == '01':
            i_cfg_sci_baud = 2400
        elif CFG1_PAR_SCIx_BAUD == '02':
            i_cfg_sci_baud = 4800
        elif CFG1_PAR_SCIx_BAUD == '03':
            i_cfg_sci_baud = 9600
        elif CFG1_PAR_SCIx_BAUD == '04':
            i_cfg_sci_baud = 19200
        elif CFG1_PAR_SCIx_BAUD == '05':
            i_cfg_sci_baud = 38400
        elif CFG1_PAR_SCIx_BAUD == '06':
            i_cfg_sci_baud = 57600
        elif CFG1_PAR_SCIx_BAUD == '07':
            i_cfg_sci_baud = 115200
        return i_cfg_sci_baud



    # sci1mode: sci1mode i CFG3_PAR_UART1_MODE
    @staticmethod
    def translate_sci1mode_to_low_level(sci1mode):
        CFG3_PAR_UART1_MODE = None
        if sci1mode == 'closed':
            CFG3_PAR_UART1_MODE = '00'
        elif sci1mode == 'kxp_aux':
            CFG3_PAR_UART1_MODE = '01'
        elif sci1mode == 'fim_main':
            CFG3_PAR_UART1_MODE = '02'
        elif sci1mode == 'uart_main':
            CFG3_PAR_UART1_MODE = '04'
        elif sci1mode == 'sfm_main':
            CFG3_PAR_UART1_MODE = '05'
        return CFG3_PAR_UART1_MODE

    @staticmethod
    def translate_sci1mode_to_high_level(CFG3_PAR_UART1_MODE):
        sci1mode = None
        if CFG3_PAR_UART1_MODE == '00':
            sci1mode = 'closed'
        elif CFG3_PAR_UART1_MODE == '01':
            sci1mode = 'kxp_aux'
        elif CFG3_PAR_UART1_MODE == '02':
            sci1mode = 'fim_main'
        elif CFG3_PAR_UART1_MODE == '04':
            sci1mode = 'uart_main'
        elif CFG3_PAR_UART1_MODE == '05':
            sci1mode = 'sfm_main'
        return sci1mode

    # sci2mode: sci2mode i CFG3_PAR_UART2_MODE
    @staticmethod
    def translate_sci2mode_to_low_level(sci2mode):
        CFG3_PAR_UART2_MODE = None
        if sci2mode == 'closed':
            CFG3_PAR_UART2_MODE = '00'
        elif sci2mode == 'kxp_main':
            CFG3_PAR_UART2_MODE = '01'
        elif sci2mode == 'fim_aux':
            CFG3_PAR_UART2_MODE = '02'
        elif sci2mode == 'uart_aux':
            CFG3_PAR_UART2_MODE = '04'
        elif sci2mode == 'sfm_aux':
            CFG3_PAR_UART2_MODE = '05'
        return CFG3_PAR_UART2_MODE

    @staticmethod
    def translate_sci2mode_to_high_level(CFG3_PAR_UART2_MODE):
        sci2mode = None
        if CFG3_PAR_UART2_MODE == '00':
            sci2mode = 'closed'
        elif CFG3_PAR_UART2_MODE == '01':
            sci2mode = 'kxp_main'
        elif CFG3_PAR_UART2_MODE == '02':
            sci2mode = 'fim_aux'
        elif CFG3_PAR_UART2_MODE == '04':
            sci2mode = 'uart_aux'
        elif CFG3_PAR_UART2_MODE == '05':
            sci2mode = 'sfm_aux'
        return sci2mode

    # dinecho01234: cfg_din_echo_n i CFG3_PAR_DIN_ECHO
    @staticmethod
    def translate_dinecho01234_to_low_level(cfg_din_echo_0, cfg_din_echo_1, cfg_din_echo_2, cfg_din_echo_3, cfg_din_echo_4):
        if cfg_din_echo_0 is None and cfg_din_echo_1 is None and  cfg_din_echo_2 is None and  cfg_din_echo_3 is None and  cfg_din_echo_4 is None:
            return None
        uc_byte = 0
        if cfg_din_echo_0:
            uc_byte |= 0x01
        if cfg_din_echo_1:
            uc_byte |= 0x02
        if cfg_din_echo_2:
            uc_byte |= 0x04
        if cfg_din_echo_3:
            uc_byte |= 0x08
        if cfg_din_echo_4:
            uc_byte |= 0x10
        return '{:02X}'.format(abs(uc_byte) & 0xff)

    @staticmethod
    def translate_dinecho01234_to_high_level(CFG3_PAR_DIN_ECHO):
        if CFG3_PAR_DIN_ECHO is None:
            return None, None, None, None, None
        try:
            uc_byte = int(CFG3_PAR_DIN_ECHO, 16)
            cfg_din_echo_0 = True if (uc_byte & 0x01 != 0) else False
            cfg_din_echo_1 = True if (uc_byte & 0x02 != 0) else False
            cfg_din_echo_2 = True if (uc_byte & 0x04 != 0) else False
            cfg_din_echo_3 = True if (uc_byte & 0x08 != 0) else False
            cfg_din_echo_4 = True if (uc_byte & 0x10 != 0) else False
            return cfg_din_echo_0, cfg_din_echo_1, cfg_din_echo_2, cfg_din_echo_3, cfg_din_echo_4
        except Exception as e:
            return None, None, None, None, None



    # ttlmode: cfg_ttl_mode i CFG3_PAR_TTLx_MODE
    @staticmethod
    def translate_ttlmode_to_low_level(cfg_ttl_mode):
        CFG3_PAR_TTLx_MODE = None
        if cfg_ttl_mode == 'closed':
            CFG3_PAR_TTLx_MODE = '00'
        elif cfg_ttl_mode == 'aba_tk2':
            CFG3_PAR_TTLx_MODE = '01'
        elif cfg_ttl_mode == 'wiegand_26':
            CFG3_PAR_TTLx_MODE = '02'
        elif cfg_ttl_mode == 'wiegand_34':
            CFG3_PAR_TTLx_MODE = '03'
        elif cfg_ttl_mode == 'wiegand_free':
            CFG3_PAR_TTLx_MODE = '04'
        return CFG3_PAR_TTLx_MODE

    @staticmethod
    def translate_ttlmode_to_high_level(CFG3_PAR_TTLx_MODE):
        cfg_ttl_mode = None
        if CFG3_PAR_TTLx_MODE == '00':
            cfg_ttl_mode = 'closed'
        elif CFG3_PAR_TTLx_MODE == '01':
            cfg_ttl_mode = 'aba_tk2'
        elif CFG3_PAR_TTLx_MODE == '02':
            cfg_ttl_mode = 'wiegand_26'
        elif CFG3_PAR_TTLx_MODE == '03':
            cfg_ttl_mode = 'wiegand_34'
        elif CFG3_PAR_TTLx_MODE == '04':
            cfg_ttl_mode = 'wiegand_free'
        return cfg_ttl_mode

    # fimoperatingbaud: cfg_sci_baud i CFG3_PAR_FIMx_OPERATING_BAUD
    @staticmethod
    def translate_fimoperatingbaud_to_low_level(i_cfg_sci_baud):
        CFG3_PAR_FIMx_OPERATING_BAUD = None
        if i_cfg_sci_baud == 9600:
            CFG3_PAR_FIMx_OPERATING_BAUD = '03'
        elif i_cfg_sci_baud == 19200:
            CFG3_PAR_FIMx_OPERATING_BAUD = '04'
        elif i_cfg_sci_baud == 38400:
            CFG3_PAR_FIMx_OPERATING_BAUD = '05'
        elif i_cfg_sci_baud == 57600:
            CFG3_PAR_FIMx_OPERATING_BAUD = '06'
        elif i_cfg_sci_baud == 115200:
            CFG3_PAR_FIMx_OPERATING_BAUD = '07'
        return CFG3_PAR_FIMx_OPERATING_BAUD

    @staticmethod
    def translate_fimoperatingbaud_to_high_level(CFG3_PAR_FIMx_OPERATING_BAUD): # cfg_sci_baud, CFG3_PAR_FIMx_OPERATING_BAUD
        i_cfg_sci_baud = None
        if CFG3_PAR_FIMx_OPERATING_BAUD == '03':
            i_cfg_sci_baud = 9600
        elif CFG3_PAR_FIMx_OPERATING_BAUD == '04':
            i_cfg_sci_baud = 19200
        elif CFG3_PAR_FIMx_OPERATING_BAUD == '05':
            i_cfg_sci_baud = 38400
        elif CFG3_PAR_FIMx_OPERATING_BAUD == '06':
            i_cfg_sci_baud = 57600
        elif CFG3_PAR_FIMx_OPERATING_BAUD == '07':
            i_cfg_sci_baud = 115200
        return i_cfg_sci_baud


    # sfmoperatingbaud: cfg_sci_baud i CFG3_PAR_SFMx_OPERATING_BAUD
    @staticmethod
    def translate_sfmoperatingbaud_to_low_level(i_cfg_sci_baud):
        CFG3_PAR_SFMx_OPERATING_BAUD = None
        if i_cfg_sci_baud == 9600:
            CFG3_PAR_SFMx_OPERATING_BAUD = '03'
        elif i_cfg_sci_baud == 19200:
            CFG3_PAR_SFMx_OPERATING_BAUD = '04'
        elif i_cfg_sci_baud == 38400:
            CFG3_PAR_SFMx_OPERATING_BAUD = '05'
        elif i_cfg_sci_baud == 57600:
            CFG3_PAR_SFMx_OPERATING_BAUD = '06'
        elif i_cfg_sci_baud == 115200:
            CFG3_PAR_SFMx_OPERATING_BAUD = '07'
        return CFG3_PAR_SFMx_OPERATING_BAUD

    @staticmethod
    def translate_sfmoperatingbaud_to_high_level(CFG3_PAR_SFMx_OPERATING_BAUD): # cfg_sci_baud, CFG3_PAR_SFMx_OPERATING_BAUD
        i_cfg_sci_baud = None
        if CFG3_PAR_SFMx_OPERATING_BAUD == '03':
            i_cfg_sci_baud = 9600
        elif CFG3_PAR_SFMx_OPERATING_BAUD == '04':
            i_cfg_sci_baud = 19200
        elif CFG3_PAR_SFMx_OPERATING_BAUD == '05':
            i_cfg_sci_baud = 38400
        elif CFG3_PAR_SFMx_OPERATING_BAUD == '06':
            i_cfg_sci_baud = 57600
        elif CFG3_PAR_SFMx_OPERATING_BAUD == '07':
            i_cfg_sci_baud = 115200
        return i_cfg_sci_baud


    # #############################################  BLOC LEXA PRINCIPAL #############################################
    # PROCEDIMENTS PUBLICS
    """
    pren un diccionari amb k:v on
        k: es el nom del paràmetre de configuració d'alt nivell del lexa main
        v: es el valor d'alt nivell que pren el paràmetre

    retorna:
        tres diccionaris f1, f2 i f3 per cada configuració del lexa main:
        k: es el número de paràmetre
        v: es el valor en format ascii-hex
        de forma que els items de dict_params queden traduits en hexa a la posició corresponent,
        i els que no s'especifiquin a dict_params es retornaràn com None
    """

    @staticmethod
    def lexamain_translate_to_low_level(dict_params):
        # inicialitzem valors de retorn
        d_f1 = {}
        d_f2 = {}
        d_f3 = {}
        for idx in range(0, 1 + 0x3f):
            d_f1[idx] = None
            d_f2[idx] = None
            d_f3[idx] = None

        # F1
        # 0x00 a 0x0f - RESERVAT
        # 0x10 - CFG1_PAR_KXP_ADDR_H (NO MODIFICAR)
        # 0x11 - CFG1_PAR_KXP_ADDR_L (NO MODIFICAR)
        # 0x12 - CFG1_PAR_SCI0_BAUD (NO MODIFICAR)
        # 0x13 - CFG1_PAR_SCI1_BAUD (NO MODIFICAR)
        # 0x14 a 0x3f - RESERVAT

        # F2
        # 0x00 a 0x3f - RESERVAT

        # F3
        # 0x00 - RESERVAT
        # 0x01 - CFG3_PAR_HOST_FE
        d_f3[0x01] = ConfigTranslator.translate_mifhostfe_to_low_level(dict_params.get('cfg_mif_host_fe'))

        # 0x02 - CFG3_PAR_UART0_MODE (NO MODIFICAR)
        # 0x03 - CFG3_PAR_UART1_MODE
        d_f3[0x03] = ConfigTranslator.translate_byte_to_low_level(0x00, 0, 255) # (Fix a 0x00)

        # 0x04 - RESERVAT
        # 0x05 - RESERVAT
        # 0x06 - CFG3_PAR_DIN_ECHO
        d_f3[0x06] = ConfigTranslator.translate_dinecho01_to_low_level(dict_params.get('exp_din_echo_0'), dict_params.get('exp_din_echo_1'))

        # 0x07 a 0x0f - RESERVAT
        # 0x10 - CFG3_PAR_MIF_MODE
        d_f3[0x10] = ConfigTranslator.translate_mifmode_to_low_level(dict_params.get('cfg_mif_mode'))

        # 0x11 - CFG3_PAR_MIF_BLOCK_NUMBER
        d_f3[0x11] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('cfg_mif_block_number'), 0, 255)

       # 0x12 - CFG3_PAR_MIF_LOGIN_MODE
        d_f3[0x12] = ConfigTranslator.translate_mifloginmode_to_low_level(dict_params.get('cfg_mif_login_mode'))

        # 0x13 - CFG3_PAR_MIF_KEY_AB
        d_f3[0x13] = ConfigTranslator.translate_mifkeyab_to_low_level(dict_params.get('cfg_mif_key_ab'))

        # 0x14 - CFG3_PAR_MIF_KEY_NUMBER
        d_f3[0x14] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('cfg_mif_key_number'), 0, 23)

        # 0x15 - CFG3_PAR_MIF_READ_OK_LED_MODE
        d_f3[0x15] = ConfigTranslator.translate_ledmode_to_low_level(dict_params.get('exp_mif_read_ok_led_mode'))

        # 0x16 - CFG3_PAR_MIF_READ_OK_LED_COLOR
        d_f3[0x16] = ConfigTranslator.translate_ledcolor_to_low_level(dict_params.get('exp_mif_read_ok_led_color'))

        # 0x17 - CFG3_PAR_MIF_READ_OK_LED_TIME_ON_10ms
        d_f3[0x17] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('exp_mif_read_ok_led_time_on_10ms'), 0, 255)

        # 0x18 - CFG3_PAR_MIF_READ_FAIL_LED_MODE
        d_f3[0x18] = ConfigTranslator.translate_ledmode_to_low_level(dict_params.get('exp_mif_read_fail_led_mode'))

        # 0x19 - CFG3_PAR_MIF_READ_FAIL_LED_COLOR
        d_f3[0x19] = ConfigTranslator.translate_ledcolor_to_low_level(dict_params.get('exp_mif_read_fail_led_color'))

        # 0x1a - CFG3_PAR_MIF_READ_FAIL_LED_TIME_ON_10ms
        d_f3[0x1a] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('exp_mif_read_fail_led_time_on_10ms'), 0, 255)

        # 0x1b - CFG3_PAR_MIF_READ_OK_BZZ_MODE
        d_f3[0x1b] = ConfigTranslator.translate_bzzmode_to_low_level(dict_params.get('exp_mif_read_ok_bzz_mode'))

        # 0x1c - CFG3_PAR_MIF_READ_OK_BZZ_TIME_ON_10ms
        d_f3[0x1c] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('exp_mif_read_ok_bzz_time_on_10ms'), 0, 255)

        # 0x1d - CFG3_PAR_MIF_READ_FAIL_BZZ_MODE
        d_f3[0x1d] = ConfigTranslator.translate_bzzmode_to_low_level(dict_params.get('exp_mif_read_fail_bzz_mode'))

        # 0x1e - CFG3_PAR_MIF_READ_FAIL_BZZ_TIME_ON_10ms
        d_f3[0x1e] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('exp_mif_read_fail_bzz_time_on_10ms'), 0, 255)

        # 0X1f - CFG3_PAR_MIF_INTER_INSTRUCTION_TMO_10ms
        d_f3[0x1f] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('cfg_mif_inter_instruction_tmo_10ms'), 20, 255)

        # 0X20 - CFG3_PAR_MIF_FIELD_OFF_DURATION_10ms
        d_f3[0x20] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('cfg_mif_field_off_duration_10ms'), 20, 255)

        # 0X21 - CFG3_PAR_MIF_KEEP_FIELD_ON_TIME_ds
        d_f3[0x21] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('cfg_mif_keep_field_on_time_ds'), 2, 255)

        #0X22 - CFG3_PAR_MIF_RX_GAIN
        d_f3[0x22] = ConfigTranslator.translate_rxgain_to_low_level(dict_params.get('cfg_mif_rx_gain'))

        # 0X23 a 0X25 - RESERVAT
        # 0X26 a 0x2e - MÒDUL SFG (NO MODIFICAR)
        # 0x2f - RESERVAT
        # 0X30 a 0X36 - MÒDUL TTG (NO MODIFICAR)
        # 0X37 a 0x39 - RESERVAT

        # 0x3A - CFG3_PAR_MIF_MSECTOR_SEL_0
        # 0x3B - CFG3_PAR_MIF_MSECTOR_SEL_1
        d_f3[0x3a], d_f3[0x3b] = ConfigTranslator.translate_msectorsel_to_low_level(dict_params.get('cfg_mif_msector_sel'))

        # 0x3C - CFG3_PAR_MIF_MSECTOR_KEYAB_0
        # 0x3D - CFG3_PAR_MIF_MSECTOR_KEYAB_1
        d_f3[0x3c], d_f3[0x3d] = ConfigTranslator.translate_msectorkeyab_to_low_level(dict_params.get('cfg_mif_msector_keyab'))

        # 0x3E a 0X3f - RESERVAT

        return d_f1, d_f2, d_f3

    @staticmethod
    def lexamain_translate_to_high_level(s_f1, s_f2, s_f3):
        # inicialitzem valors de retorn
        dict_params = {}

        try:
            d_f1 = {}
            d_f2 = {}
            d_f3 = {}
            for idx in range(0, 1 + 0x3f):
                d_f1[idx] = s_f1[2 * idx:2 * idx + 2].lower()
                d_f2[idx] = s_f2[2 * idx:2 * idx + 2].lower()
                d_f3[idx] = s_f3[2 * idx:2 * idx + 2].lower()
        except Exception as e:
            return dict_params

        # F1
        # 0x00 a 0x0f - RESERVAT
        # 0x10 - CFG1_PAR_KXP_ADDR_H (NO MODIFICAR)
        # 0x11 - CFG1_PAR_KXP_ADDR_L (NO MODIFICAR)
        # 0x12 - CFG1_PAR_SCI0_BAUD (NO MODIFICAR)
        # 0x13 - CFG1_PAR_SCI1_BAUD (NO MODIFICAR)
        # 0x14 a 0x3f - RESERVAT

        # F2
        # 0x00 a 0x3f - RESERVAT

        # F3
        # 0x00 - RESERVAT
        # 0x01 - CFG3_PAR_HOST_FE
        tmp = ConfigTranslator.translate_mifhostfe_to_high_level(d_f3[0x01])
        if tmp is not None:
            dict_params['cfg_mif_host_fe'] = tmp

        # 0x02 - CFG3_PAR_UART0_MODE (NO MODIFICAR)
        # 0x03 - CFG3_PAR_UART1_MODE (Fix a 0x00)

        # 0x04 - RESERVAT
        # 0x05 - RESERVAT
        # 0x06 - CFG3_PAR_DIN_ECHO
        tmp_0, tmp_1 = ConfigTranslator.translate_dinecho01_to_high_level(d_f3[0x06])
        if tmp_0 is not None:
            dict_params['exp_din_echo_0'] = tmp_0
        if tmp_1 is not None:
            dict_params['exp_din_echo_1'] = tmp_1

        # 0x07 a 0x0f - RESERVAT
        # 0x10 - CFG3_PAR_MIF_MODE
        tmp = ConfigTranslator.translate_mifmode_to_high_level(d_f3[0x10])
        if tmp is not None:
            dict_params['cfg_mif_mode'] = tmp

        # 0x11 - CFG3_PAR_MIF_BLOCK_NUMBER
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x11])
        if tmp is not None:
            dict_params['cfg_mif_block_number'] = tmp

        # 0x12 - CFG3_PAR_MIF_LOGIN_MODE
        tmp = ConfigTranslator.translate_mifloginmode_to_high_level(d_f3[0x12])
        if tmp is not None:
            dict_params['cfg_mif_login_mode'] = tmp

        # 0x13 - CFG3_PAR_MIF_KEY_AB
        tmp = ConfigTranslator.translate_mifkeyab_to_high_level(d_f3[0x13])
        if tmp is not None:
            dict_params['cfg_mif_key_ab'] = tmp

        # 0x14 - CFG3_PAR_MIF_KEY_NUMBER
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x14])
        if tmp is not None:
            dict_params['cfg_mif_key_number'] = tmp

        # 0x15 - CFG3_PAR_MIF_READ_OK_LED_MODE
        tmp = ConfigTranslator.translate_ledmode_to_high_level(d_f3[0x15])
        if tmp is not None:
            dict_params['exp_mif_read_ok_led_mode'] = tmp

        # 0x16 - CFG3_PAR_MIF_READ_OK_LED_COLOR
        tmp = ConfigTranslator.translate_ledcolor_to_high_level(d_f3[0x16])
        if tmp is not None:
            dict_params['exp_mif_read_ok_led_color'] = tmp

        # 0x17 - CFG3_PAR_MIF_READ_OK_LED_TIME_ON_10ms
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x17])
        if tmp is not None:
            dict_params['exp_mif_read_ok_led_time_on_10ms'] = tmp

        # 0x18 - CFG3_PAR_MIF_READ_FAIL_LED_MODE
        tmp = ConfigTranslator.translate_ledmode_to_high_level(d_f3[0x18])
        if tmp is not None:
            dict_params['exp_mif_read_fail_led_mode'] = tmp

        # 0x19 - CFG3_PAR_MIF_READ_FAIL_LED_COLOR
        tmp = ConfigTranslator.translate_ledcolor_to_high_level(d_f3[0x19])
        if tmp is not None:
            dict_params['exp_mif_read_fail_led_color'] = tmp

        # 0x1a - CFG3_PAR_MIF_READ_FAIL_LED_TIME_ON_10ms
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x1a])
        if tmp is not None:
            dict_params['exp_mif_read_fail_led_time_on_10ms'] = tmp

        # 0x1b - CFG3_PAR_MIF_READ_OK_BZZ_MODE
        tmp = ConfigTranslator.translate_bzzmode_to_high_level(d_f3[0x1b])
        if tmp is not None:
            dict_params['exp_mif_read_ok_bzz_mode'] = tmp

        # 0x1c - CFG3_PAR_MIF_READ_OK_BZZ_TIME_ON_10ms
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x1c])
        if tmp is not None:
            dict_params['exp_mif_read_ok_bzz_time_on_10ms'] = tmp

        # 0x1d - CFG3_PAR_MIF_READ_FAIL_BZZ_MODE
        tmp = ConfigTranslator.translate_bzzmode_to_high_level(d_f3[0x1d])
        if tmp is not None:
            dict_params['exp_mif_read_fail_bzz_mode'] = tmp

        # 0x1e - CFG3_PAR_MIF_READ_FAIL_BZZ_TIME_ON_10ms
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x1e])
        if tmp is not None:
            dict_params['exp_mif_read_fail_bzz_time_on_10ms'] = tmp

        # 0X1f - CFG3_PAR_MIF_INTER_INSTRUCTION_TMO_10ms
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x1f])
        if tmp is not None:
            dict_params['cfg_mif_inter_instruction_tmo_10ms'] = tmp

        # 0X20 - CFG3_PAR_MIF_FIELD_OFF_DURATION_10ms
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x20])
        if tmp is not None:
            dict_params['cfg_mif_field_off_duration_10ms'] = tmp

        # 0X21 - CFG3_PAR_MIF_KEEP_FIELD_ON_TIME_ds
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x21])
        if tmp is not None:
            dict_params['cfg_mif_keep_field_on_time_ds'] = tmp

        # 0X22 - CFG3_PAR_MIF_RX_GAIN
        tmp = ConfigTranslator.translate_rxgain_to_high_level(d_f3[0x22])
        if tmp is not None:
            dict_params['cfg_mif_rx_gain'] = tmp

        # 0X23 a 0X25 - RESERVAT
        # 0X26 a 0x2e - MÒDUL SFG (NO MODIFICAR)
        # 0x2f - RESERVAT
        # 0X30 a 0X36 - MÒDUL TTG (NO MODIFICAR)
        # 0X37 a 0x39 - RESERVAT

        # 0x3A - CFG3_PAR_MIF_MSECTOR_SEL_0
        # 0x3B - CFG3_PAR_MIF_MSECTOR_SEL_1
        tmp = ConfigTranslator.translate_msectorsel_to_high_level(d_f3[0x3a], d_f3[0x3b])
        if tmp is not None:
            dict_params['cfg_mif_msector_sel'] = tmp

        # 0x3C - CFG3_PAR_MIF_MSECTOR_KEYAB_0
        # 0x3D - CFG3_PAR_MIF_MSECTOR_KEYAB_1
        tmp = ConfigTranslator.translate_msectorkeyab_to_high_level(d_f3[0x3c], d_f3[0x3d])
        if tmp is not None:
            dict_params['cfg_mif_msector_keyab'] = tmp

        # 0X3e a 0X3f - RESERVAT

        return dict_params

    # #############################################  BLOC LEXA AUXILIAR #############################################
    # PROCEDIMENTS PUBLICS
    """
    pren un diccionari amb k:v on
        k: es el nom del paràmetre de configuració d'alt nivell del lexa aux
        v: es el valor d'alt nivell que pren el paràmetre

    retorna:
        tres diccionaris f1, f2 i f3 per cada configuració del lexa aux:
        k: es el número de paràmetre
        v: es el valor en format ascii-hex
        de forma que els items de dict_params queden traduits en hexa a la posició corresponent,
        i els que no s'especifiquin a dict_params es retornaràn com None
    """

    @staticmethod
    def lexaaux_translate_to_low_level(dict_params):
        # inicialitzem valors de retorn
        d_f1 = {}
        d_f2 = {}
        d_f3 = {}
        for idx in range(0, 1 + 0x3f):
            d_f1[idx] = None
            d_f2[idx] = None
            d_f3[idx] = None

        # F1
        # 0x00 a 0x0f - RESERVAT
        # 0x10 - CFG1_PAR_KXP_ADDR_H (NO MODIFICAR)
        # 0x11 - CFG1_PAR_KXP_ADDR_L (NO MODIFICAR)
        # 0x12 - CFG1_PAR_SCI0_BAUD (NO MODIFICAR)
        # 0x13 - CFG1_PAR_SCI1_BAUD (NO MODIFICAR)
        # 0x14 a 0x3f - RESERVAT

        # F2
        # 0x00 a 0x3f - RESERVAT

        # F3
        # 0x00 - RESERVAT
        # 0x01 - CFG3_PAR_HOST_FE
        d_f3[0x01] = ConfigTranslator.translate_mifhostfe_to_low_level(dict_params.get('aux_mif_host_fe'))

        # 0x02 - CFG3_PAR_UART0_MODE (NO MODIFICAR)
        # 0x03 - CFG3_PAR_UART1_MODE
        d_f3[0x03] = ConfigTranslator.translate_byte_to_low_level(0x00, 0, 255) # (Fix a 0x00)

        # 0x04 - RESERVAT
        # 0x05 - RESERVAT
        # 0x06 - CFG3_PAR_DIN_ECHO
        d_f3[0x06] = ConfigTranslator.translate_dinecho01_to_low_level(dict_params.get('aux_din_echo_0'), dict_params.get('aux_din_echo_1'))

        # 0x07 a 0x0f - RESERVAT
        # 0x10 - CFG3_PAR_MIF_MODE
        d_f3[0x10] = ConfigTranslator.translate_mifmode_to_low_level(dict_params.get('aux_mif_mode'))

        # 0x11 - CFG3_PAR_MIF_BLOCK_NUMBER
        d_f3[0x11] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('aux_mif_block_number'), 0, 255)

       # 0x12 - CFG3_PAR_MIF_LOGIN_MODE
        d_f3[0x12] = ConfigTranslator.translate_mifloginmode_to_low_level(dict_params.get('aux_mif_login_mode'))

        # 0x13 - CFG3_PAR_MIF_KEY_AB
        d_f3[0x13] = ConfigTranslator.translate_mifkeyab_to_low_level(dict_params.get('aux_mif_key_ab'))

        # 0x14 - CFG3_PAR_MIF_KEY_NUMBER
        d_f3[0x14] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('aux_mif_key_number'), 0, 23)

        # 0x15 - CFG3_PAR_MIF_READ_OK_LED_MODE
        d_f3[0x15] = ConfigTranslator.translate_ledmode_to_low_level(dict_params.get('aux_mif_read_ok_led_mode'))

        # 0x16 - CFG3_PAR_MIF_READ_OK_LED_COLOR
        d_f3[0x16] = ConfigTranslator.translate_ledcolor_to_low_level(dict_params.get('aux_mif_read_ok_led_color'))

        # 0x17 - CFG3_PAR_MIF_READ_OK_LED_TIME_ON_10ms
        d_f3[0x17] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('aux_mif_read_ok_led_time_on_10ms'), 0, 255)

        # 0x18 - CFG3_PAR_MIF_READ_FAIL_LED_MODE
        d_f3[0x18] = ConfigTranslator.translate_ledmode_to_low_level(dict_params.get('aux_mif_read_fail_led_mode'))

        # 0x19 - CFG3_PAR_MIF_READ_FAIL_LED_COLOR
        d_f3[0x19] = ConfigTranslator.translate_ledcolor_to_low_level(dict_params.get('aux_mif_read_fail_led_color'))

        # 0x1a - CFG3_PAR_MIF_READ_FAIL_LED_TIME_ON_10ms
        d_f3[0x1a] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('aux_mif_read_fail_led_time_on_10ms'), 0, 255)

        # 0x1b - CFG3_PAR_MIF_READ_OK_BZZ_MODE
        d_f3[0x1b] = ConfigTranslator.translate_bzzmode_to_low_level(dict_params.get('aux_mif_read_ok_bzz_mode'))

        # 0x1c - CFG3_PAR_MIF_READ_OK_BZZ_TIME_ON_10ms
        d_f3[0x1c] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('aux_mif_read_ok_bzz_time_on_10ms'), 0, 255)

        # 0x1d - CFG3_PAR_MIF_READ_FAIL_BZZ_MODE
        d_f3[0x1d] = ConfigTranslator.translate_bzzmode_to_low_level(dict_params.get('aux_mif_read_fail_bzz_mode'))

        # 0x1e - CFG3_PAR_MIF_READ_FAIL_BZZ_TIME_ON_10ms
        d_f3[0x1e] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('aux_mif_read_fail_bzz_time_on_10ms'), 0, 255)

        # 0X1f - CFG3_PAR_MIF_INTER_INSTRUCTION_TMO_10ms
        d_f3[0x1f] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('aux_mif_inter_instruction_tmo_10ms'), 20, 255)

        # 0X20 - CFG3_PAR_MIF_FIELD_OFF_DURATION_10ms
        d_f3[0x20] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('aux_mif_field_off_duration_10ms'), 20, 255)

        # 0X21 - CFG3_PAR_MIF_KEEP_FIELD_ON_TIME_ds
        d_f3[0x21] = ConfigTranslator.translate_byte_to_low_level(dict_params.get('aux_mif_keep_field_on_time_ds'), 2, 255)

        #0X22 - CFG3_PAR_MIF_RX_GAIN
        d_f3[0x22] = ConfigTranslator.translate_rxgain_to_low_level(dict_params.get('aux_mif_rx_gain'))

        # 0X23 a 0X25 - RESERVAT
        # 0X26 a 0x2e - MÒDUL SFG (NO MODIFICAR)
        # 0x2f - RESERVAT
        # 0X30 a 0X36 - MÒDUL TTG (NO MODIFICAR)
        # 0X37 a 0x39 - RESERVAT

        # 0x3A - CFG3_PAR_MIF_MSECTOR_SEL_0
        # 0x3B - CFG3_PAR_MIF_MSECTOR_SEL_1
        d_f3[0x3a], d_f3[0x3b] = ConfigTranslator.translate_msectorsel_to_low_level(dict_params.get('aux_mif_msector_sel'))

        # 0x3C - CFG3_PAR_MIF_MSECTOR_KEYAB_0
        # 0x3D - CFG3_PAR_MIF_MSECTOR_KEYAB_1
        d_f3[0x3c], d_f3[0x3d] = ConfigTranslator.translate_msectorkeyab_to_low_level(dict_params.get('aux_mif_msector_keyab'))

        # 0x3E a 0X3f - RESERVAT

        return d_f1, d_f2, d_f3

    @staticmethod
    def lexaaux_translate_to_high_level(s_f1, s_f2, s_f3):
        # inicialitzem valors de retorn
        dict_params = {}

        try:
            d_f1 = {}
            d_f2 = {}
            d_f3 = {}
            for idx in range(0, 1 + 0x3f):
                d_f1[idx] = s_f1[2 * idx:2 * idx + 2].lower()
                d_f2[idx] = s_f2[2 * idx:2 * idx + 2].lower()
                d_f3[idx] = s_f3[2 * idx:2 * idx + 2].lower()
        except Exception as e:
            return dict_params

        # F1
        # 0x00 a 0x0f - RESERVAT
        # 0x10 - CFG1_PAR_KXP_ADDR_H (NO MODIFICAR)
        # 0x11 - CFG1_PAR_KXP_ADDR_L (NO MODIFICAR)
        # 0x12 - CFG1_PAR_SCI0_BAUD (NO MODIFICAR)
        # 0x13 - CFG1_PAR_SCI1_BAUD (NO MODIFICAR)
        # 0x14 a 0x3f - RESERVAT

        # F2
        # 0x00 a 0x3f - RESERVAT

        # F3
        # 0x00 - RESERVAT
        # 0x01 - CFG3_PAR_HOST_FE
        tmp = ConfigTranslator.translate_mifhostfe_to_high_level(d_f3[0x01])
        if tmp is not None:
            dict_params['aux_mif_host_fe'] = tmp

        # 0x02 - CFG3_PAR_UART0_MODE (NO MODIFICAR)
        # 0x03 - CFG3_PAR_UART1_MODE (Fix a 0x00)

        # 0x04 - RESERVAT
        # 0x05 - RESERVAT
        # 0x06 - CFG3_PAR_DIN_ECHO
        tmp_0, tmp_1 = ConfigTranslator.translate_dinecho01_to_high_level(d_f3[0x06])
        if tmp_0 is not None:
            dict_params['aux_din_echo_0'] = tmp_0
        if tmp_1 is not None:
            dict_params['aux_din_echo_1'] = tmp_1

        # 0x07 a 0x0f - RESERVAT
        # 0x10 - CFG3_PAR_MIF_MODE
        tmp = ConfigTranslator.translate_mifmode_to_high_level(d_f3[0x10])
        if tmp is not None:
            dict_params['aux_mif_mode'] = tmp

        # 0x11 - CFG3_PAR_MIF_BLOCK_NUMBER
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x11])
        if tmp is not None:
            dict_params['aux_mif_block_number'] = tmp

        # 0x12 - CFG3_PAR_MIF_LOGIN_MODE
        tmp = ConfigTranslator.translate_mifloginmode_to_high_level(d_f3[0x12])
        if tmp is not None:
            dict_params['aux_mif_login_mode'] = tmp

        # 0x13 - CFG3_PAR_MIF_KEY_AB
        tmp = ConfigTranslator.translate_mifkeyab_to_high_level(d_f3[0x13])
        if tmp is not None:
            dict_params['aux_mif_key_ab'] = tmp

        # 0x14 - CFG3_PAR_MIF_KEY_NUMBER
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x14])
        if tmp is not None:
            dict_params['aux_mif_key_number'] = tmp

        # 0x15 - CFG3_PAR_MIF_READ_OK_LED_MODE
        tmp = ConfigTranslator.translate_ledmode_to_high_level(d_f3[0x15])
        if tmp is not None:
            dict_params['aux_mif_read_ok_led_mode'] = tmp

        # 0x16 - CFG3_PAR_MIF_READ_OK_LED_COLOR
        tmp = ConfigTranslator.translate_ledcolor_to_high_level(d_f3[0x16])
        if tmp is not None:
            dict_params['aux_mif_read_ok_led_color'] = tmp

        # 0x17 - CFG3_PAR_MIF_READ_OK_LED_TIME_ON_10ms
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x17])
        if tmp is not None:
            dict_params['aux_mif_read_ok_led_time_on_10ms'] = tmp

        # 0x18 - CFG3_PAR_MIF_READ_FAIL_LED_MODE
        tmp = ConfigTranslator.translate_ledmode_to_high_level(d_f3[0x18])
        if tmp is not None:
            dict_params['aux_mif_read_fail_led_mode'] = tmp

        # 0x19 - CFG3_PAR_MIF_READ_FAIL_LED_COLOR
        tmp = ConfigTranslator.translate_ledcolor_to_high_level(d_f3[0x19])
        if tmp is not None:
            dict_params['aux_mif_read_fail_led_color'] = tmp

        # 0x1a - CFG3_PAR_MIF_READ_FAIL_LED_TIME_ON_10ms
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x1a])
        if tmp is not None:
            dict_params['aux_mif_read_fail_led_time_on_10ms'] = tmp

        # 0x1b - CFG3_PAR_MIF_READ_OK_BZZ_MODE
        tmp = ConfigTranslator.translate_bzzmode_to_high_level(d_f3[0x1b])
        if tmp is not None:
            dict_params['aux_mif_read_ok_bzz_mode'] = tmp

        # 0x1c - CFG3_PAR_MIF_READ_OK_BZZ_TIME_ON_10ms
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x1c])
        if tmp is not None:
            dict_params['aux_mif_read_ok_bzz_time_on_10ms'] = tmp

        # 0x1d - CFG3_PAR_MIF_READ_FAIL_BZZ_MODE
        tmp = ConfigTranslator.translate_bzzmode_to_high_level(d_f3[0x1d])
        if tmp is not None:
            dict_params['aux_mif_read_fail_bzz_mode'] = tmp

        # 0x1e - CFG3_PAR_MIF_READ_FAIL_BZZ_TIME_ON_10ms
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x1e])
        if tmp is not None:
            dict_params['aux_mif_read_fail_bzz_time_on_10ms'] = tmp

        # 0X1f - CFG3_PAR_MIF_INTER_INSTRUCTION_TMO_10ms
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x1f])
        if tmp is not None:
            dict_params['aux_mif_inter_instruction_tmo_10ms'] = tmp

        # 0X20 - CFG3_PAR_MIF_FIELD_OFF_DURATION_10ms
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x20])
        if tmp is not None:
            dict_params['aux_mif_field_off_duration_10ms'] = tmp

        # 0X21 - CFG3_PAR_MIF_KEEP_FIELD_ON_TIME_ds
        tmp = ConfigTranslator.translate_byte_to_high_level(d_f3[0x21])
        if tmp is not None:
            dict_params['aux_mif_keep_field_on_time_ds'] = tmp

        # 0X22 - CFG3_PAR_MIF_RX_GAIN
        tmp = ConfigTranslator.translate_rxgain_to_high_level(d_f3[0x22])
        if tmp is not None:
            dict_params['aux_mif_rx_gain'] = tmp

        # 0X23 a 0X25 - RESERVAT
        # 0X26 a 0x2e - MÒDUL SFG (NO MODIFICAR)
        # 0x2f - RESERVAT
        # 0X30 a 0X36 - MÒDUL TTG (NO MODIFICAR)
        # 0X37 a 0x39 - RESERVAT

        # 0x3A - CFG3_PAR_MIF_MSECTOR_SEL_0
        # 0x3B - CFG3_PAR_MIF_MSECTOR_SEL_1
        tmp = ConfigTranslator.translate_msectorsel_to_high_level(d_f3[0x3a], d_f3[0x3b])
        if tmp is not None:
            dict_params['aux_mif_msector_sel'] = tmp

        # 0x3C - CFG3_PAR_MIF_MSECTOR_KEYAB_0
        # 0x3D - CFG3_PAR_MIF_MSECTOR_KEYAB_1
        tmp = ConfigTranslator.translate_msectorkeyab_to_high_level(d_f3[0x3c], d_f3[0x3d])
        if tmp is not None:
            dict_params['aux_mif_msector_keyab'] = tmp

        # 0X3e a 0X3f - RESERVAT

        return dict_params

    # #######################################  BLOC COMU LEXA PRINCIPAL/AUXILIAR #######################################

    # ##############################################################
    # mètodes interns PRIVATS. No fer servir des de fora de la classe
    # ##############################################################

    # dinecho01: cfg_din_echo_n i CFG3_PAR_DIN_ECHO
    @staticmethod
    def translate_dinecho01_to_low_level(cfg_din_echo_0, cfg_din_echo_1):
        if cfg_din_echo_0 is None and cfg_din_echo_1 is None:
            return None
        uc_byte = 0
        if cfg_din_echo_0:
            uc_byte |= 0x01
        if cfg_din_echo_1:
            uc_byte |= 0x02
        return '{:02X}'.format(abs(uc_byte) & 0xff)

    @staticmethod
    def translate_dinecho01_to_high_level(CFG3_PAR_DIN_ECHO):
        if CFG3_PAR_DIN_ECHO is None:
            return None, None
        try:
            uc_byte = int(CFG3_PAR_DIN_ECHO, 16)
            cfg_din_echo_0 = True if (uc_byte & 0x01 != 0) else False
            cfg_din_echo_1 = True if (uc_byte & 0x02 != 0) else False
            return cfg_din_echo_0, cfg_din_echo_1
        except Exception as e:
            return None, None

    # mifhostfe: cfg_mif_host_fe i CFG3_PAR_HOST_FE
    @staticmethod
    def translate_mifhostfe_to_low_level(cfg_mif_host_fe):
        CFG3_PAR_HOST_FE = None
        if cfg_mif_host_fe == 'J2':
            CFG3_PAR_HOST_FE = '00'
        elif cfg_mif_host_fe == 'J1':
            CFG3_PAR_HOST_FE = '01'
        return CFG3_PAR_HOST_FE

    @staticmethod
    def translate_mifhostfe_to_high_level(CFG3_PAR_HOST_FE):
        cfg_mif_host_fe = None
        if CFG3_PAR_HOST_FE == '00':
            cfg_mif_host_fe = 'J2'
        elif CFG3_PAR_HOST_FE == '01':
            cfg_mif_host_fe = 'J1'
        return cfg_mif_host_fe

    # mifmode: cfg_mif_mode i CFG3_PAR_MIF_MODE
    @staticmethod
    def translate_mifmode_to_low_level(cfg_mif_mode):
        CFG3_PAR_MIF_MODE = None
        if cfg_mif_mode == 'disabled':
            CFG3_PAR_MIF_MODE = '00'
        elif cfg_mif_mode == 'atqa_uid':
            CFG3_PAR_MIF_MODE = '01'
        elif cfg_mif_mode == 'one_block':
            CFG3_PAR_MIF_MODE = '02'
        elif cfg_mif_mode == 'three_blocks':
            CFG3_PAR_MIF_MODE = '03'
        elif cfg_mif_mode == 'desfire_file':
            CFG3_PAR_MIF_MODE = '04'
        elif cfg_mif_mode == 'multisector':
            CFG3_PAR_MIF_MODE = '05'
        elif cfg_mif_mode == 'reversed_atqa_uid':
            CFG3_PAR_MIF_MODE = '11'
        elif cfg_mif_mode == 'mad_one_block':
            CFG3_PAR_MIF_MODE = '12'
        elif cfg_mif_mode == 'mad_three_blocks':
            CFG3_PAR_MIF_MODE = '13'
        return CFG3_PAR_MIF_MODE

    @staticmethod
    def translate_mifmode_to_high_level(CFG3_PAR_MIF_MODE):
        cfg_mif_mode = None
        if CFG3_PAR_MIF_MODE == '00':
            cfg_mif_mode = 'disabled'
        elif CFG3_PAR_MIF_MODE == '01':
            cfg_mif_mode = 'atqa_uid'
        elif CFG3_PAR_MIF_MODE == '02':
            cfg_mif_mode = 'one_block'
        elif CFG3_PAR_MIF_MODE == '03':
            cfg_mif_mode = 'three_blocks'
        elif CFG3_PAR_MIF_MODE == '04':
            cfg_mif_mode = 'desfire_file'
        elif CFG3_PAR_MIF_MODE == '05':
            cfg_mif_mode = 'multisector'
        elif CFG3_PAR_MIF_MODE == '11':
            cfg_mif_mode = 'reversed_atqa_uid'
        elif CFG3_PAR_MIF_MODE == '12':
            cfg_mif_mode = 'mad_one_block'
        elif CFG3_PAR_MIF_MODE == '13':
            cfg_mif_mode = 'mad_three_blocks'
        return cfg_mif_mode

    # bytes en rang
    @staticmethod
    def translate_byte_to_low_level(uc_byte, uc_min, uc_max):
        if uc_byte is None or uc_min is None or uc_max is None:
            return None
        if uc_min < 0:
            return None
        if uc_max > 255:
            return None
        if uc_min > uc_max:
            return None
        if uc_byte < uc_min:
            return None
        if uc_byte > uc_max:
            return None
        return '{:02X}'.format(abs(uc_byte) & 0xff)

    @staticmethod
    def translate_byte_to_high_level(s_byte):
        return int(s_byte, 16)

    # mifloginmode: cfg_mif_login_mode i CFG3_PAR_MIF_LOGIN_MODE
    @staticmethod
    def translate_mifloginmode_to_low_level(cfg_mif_login_mode):
        CFG3_PAR_MIF_LOGIN_MODE = None
        if cfg_mif_login_mode == 'never':
            CFG3_PAR_MIF_LOGIN_MODE = '00'
        elif cfg_mif_login_mode == 'always':
            CFG3_PAR_MIF_LOGIN_MODE = '01'
        elif cfg_mif_login_mode == 'auto':
            CFG3_PAR_MIF_LOGIN_MODE = '02'
        return CFG3_PAR_MIF_LOGIN_MODE


    @staticmethod
    def translate_mifloginmode_to_high_level(CFG3_PAR_MIF_LOGIN_MODE):
        cfg_mif_login_mode = None
        if CFG3_PAR_MIF_LOGIN_MODE == '00':
            cfg_mif_login_mode = 'never'
        elif CFG3_PAR_MIF_LOGIN_MODE == '01':
            cfg_mif_login_mode = 'always'
        elif CFG3_PAR_MIF_LOGIN_MODE == '02':
            cfg_mif_login_mode = 'auto'
        return cfg_mif_login_mode


    # mifkeyab: cfg_mif_key_ab i CFG3_PAR_MIF_KEY_AB
    @staticmethod
    def translate_mifkeyab_to_low_level(cfg_mif_key_ab):
        CFG3_PAR_MIF_KEY_AB = None
        if cfg_mif_key_ab == 'keya_isoauth':
            CFG3_PAR_MIF_KEY_AB = '00'
        elif cfg_mif_key_ab == 'keyb_natauth':
            CFG3_PAR_MIF_KEY_AB = '01'
        return CFG3_PAR_MIF_KEY_AB


    @staticmethod
    def translate_mifkeyab_to_high_level(CFG3_PAR_MIF_KEY_AB):
        cfg_mif_key_ab = None
        if CFG3_PAR_MIF_KEY_AB == '00':
            cfg_mif_key_ab = 'keya_isoauth'
        elif CFG3_PAR_MIF_KEY_AB == '01':
            cfg_mif_key_ab = 'keyb_natauth'
        return cfg_mif_key_ab


    # ledmode: cfg_led_mode i CFGx_PAR_LED_MODE
    @staticmethod
    def translate_ledmode_to_low_level(cfg_led_mode):
        CFGx_PAR_LED_MODE = None
        if cfg_led_mode == 'off':
            CFGx_PAR_LED_MODE = '00'
        elif cfg_led_mode == 'on':
            CFGx_PAR_LED_MODE = '01'
        elif cfg_led_mode == 'flash_30':
            CFGx_PAR_LED_MODE = '02'
        elif cfg_led_mode == 'flash_50':
            CFGx_PAR_LED_MODE = '03'
        elif cfg_led_mode == 'flash_70':
            CFGx_PAR_LED_MODE = '04'
        return CFGx_PAR_LED_MODE

    @staticmethod
    def translate_ledmode_to_high_level(CFGx_PAR_LED_MODE):
        cfg_led_mode = None
        if CFGx_PAR_LED_MODE == '00':
            cfg_led_mode = 'off'
        elif CFGx_PAR_LED_MODE == '01':
            cfg_led_mode = 'on'
        elif CFGx_PAR_LED_MODE == '02':
            cfg_led_mode = 'flash_30'
        elif CFGx_PAR_LED_MODE == '03':
            cfg_led_mode = 'flash_50'
        elif CFGx_PAR_LED_MODE == '04':
            cfg_led_mode = 'flash_70'
        return cfg_led_mode


    # ledcolor: cfg_led_color i CFGx_PAR_LED_COLOR
    @staticmethod
    def translate_ledcolor_to_low_level(cfg_led_color):
        CFGx_PAR_LED_COLOR = None
        if cfg_led_color == 'black':
            CFGx_PAR_LED_COLOR = '00'
        elif cfg_led_color == 'red':
            CFGx_PAR_LED_COLOR = '01'
        elif cfg_led_color == 'green':
            CFGx_PAR_LED_COLOR = '02'
        elif cfg_led_color == 'orange':
            CFGx_PAR_LED_COLOR = '03'
        elif cfg_led_color == 'blue':
            CFGx_PAR_LED_COLOR = '04'
        elif cfg_led_color == 'purple':
            CFGx_PAR_LED_COLOR = '05'
        elif cfg_led_color == 'cyan':
            CFGx_PAR_LED_COLOR = '06'
        elif cfg_led_color == 'white':
            CFGx_PAR_LED_COLOR = '07'
        return CFGx_PAR_LED_COLOR

    @staticmethod
    def translate_ledcolor_to_high_level(CFGx_PAR_LED_COLOR):
        cfg_led_color = None
        if CFGx_PAR_LED_COLOR == '00':
            cfg_led_color = 'black'
        elif CFGx_PAR_LED_COLOR == '01':
            cfg_led_color = 'red'
        elif CFGx_PAR_LED_COLOR == '02':
            cfg_led_color = 'green'
        elif CFGx_PAR_LED_COLOR == '03':
            cfg_led_color = 'orange'
        elif CFGx_PAR_LED_COLOR == '04':
            cfg_led_color = 'blue'
        elif CFGx_PAR_LED_COLOR == '05':
            cfg_led_color = 'purple'
        elif CFGx_PAR_LED_COLOR == '06':
            cfg_led_color = 'cyan'
        elif CFGx_PAR_LED_COLOR == '07':
            cfg_led_color = 'white'
        return cfg_led_color

    # bzzmode: cfg_bzz_mode i CFGx_PAR_BZZ_MODE
    @staticmethod
    def translate_bzzmode_to_low_level(cfg_bzz_mode):
        CFGx_PAR_BZZ_MODE = None
        if cfg_bzz_mode == 'off':
            CFGx_PAR_BZZ_MODE = '00'
        elif cfg_bzz_mode == 'on':
            CFGx_PAR_BZZ_MODE = '01'
        elif cfg_bzz_mode == 'beep_30':
            CFGx_PAR_BZZ_MODE = '02'
        elif cfg_bzz_mode == 'beep_50':
            CFGx_PAR_BZZ_MODE = '03'
        elif cfg_bzz_mode == 'beep_70':
            CFGx_PAR_BZZ_MODE = '04'
        return CFGx_PAR_BZZ_MODE

    @staticmethod
    def translate_bzzmode_to_high_level(CFGx_PAR_BZZ_MODE):
        cfg_bzz_mode = None
        if CFGx_PAR_BZZ_MODE == '00':
            cfg_bzz_mode = 'off'
        elif CFGx_PAR_BZZ_MODE == '01':
            cfg_bzz_mode = 'on'
        elif CFGx_PAR_BZZ_MODE == '02':
            cfg_bzz_mode = 'beep_30'
        elif CFGx_PAR_BZZ_MODE == '03':
            cfg_bzz_mode = 'beep_50'
        elif CFGx_PAR_BZZ_MODE == '04':
            cfg_bzz_mode = 'beep_70'
        return cfg_bzz_mode

    # rxgain: cfg_mif_rx_gain i CFG3_PAR_MIF_RX_GAIN
    @staticmethod
    def translate_rxgain_to_low_level(cfg_mif_rx_gain):
        CFG3_PAR_MIF_RX_GAIN = None
        if cfg_mif_rx_gain == '30db':
            CFG3_PAR_MIF_RX_GAIN = '00'
        elif cfg_mif_rx_gain == '40db':
            CFG3_PAR_MIF_RX_GAIN = '01'
        elif cfg_mif_rx_gain == '50db':
            CFG3_PAR_MIF_RX_GAIN = '02'
        elif cfg_mif_rx_gain == '60db':
            CFG3_PAR_MIF_RX_GAIN = '03'
        return CFG3_PAR_MIF_RX_GAIN

    @staticmethod
    def translate_rxgain_to_high_level(CFG3_PAR_MIF_RX_GAIN):
        cfg_mif_rx_gain = None
        if CFG3_PAR_MIF_RX_GAIN == '00':
            cfg_mif_rx_gain = '30db'
        elif CFG3_PAR_MIF_RX_GAIN == '01':
            cfg_mif_rx_gain = '40db'
        elif CFG3_PAR_MIF_RX_GAIN == '02':
            cfg_mif_rx_gain = '50db'
        elif CFG3_PAR_MIF_RX_GAIN == '03':
            cfg_mif_rx_gain = '60db'
        return cfg_mif_rx_gain

    @staticmethod
    def translate_msectorsel_to_low_level(cfg_mif_msector_sel):
        CFG3_PAR_MIF_MSECTOR_SEL_0 = None
        CFG3_PAR_MIF_MSECTOR_SEL_1 = None
        if cfg_mif_msector_sel is not None:
            # cfg_mif_msector_sel ha de ser una cadena de 16 '0' o '1' separada per comes.
            sectors_list = [x.strip() for x in cfg_mif_msector_sel.split(',') if x != '']
            binary_string = ''.join(['1' if bit == '1' else '0' for bit in reversed(sectors_list)])
            number = int(binary_string, 2)
            hex_string = format(number, '04X')
            CFG3_PAR_MIF_MSECTOR_SEL_0 = hex_string[2:]
            CFG3_PAR_MIF_MSECTOR_SEL_1 = hex_string[:2]
        return CFG3_PAR_MIF_MSECTOR_SEL_0, CFG3_PAR_MIF_MSECTOR_SEL_1

    @staticmethod
    def translate_msectorsel_to_high_level(CFG3_PAR_MIF_MSECTOR_SEL_0, CFG3_PAR_MIF_MSECTOR_SEL_1):
        # CFG3_PAR_MIF_MSECTOR_SEL_0 / 1 han de ser cadenes hexadecimals de 2 dígits
        low_byte = CFG3_PAR_MIF_MSECTOR_SEL_0
        high_byte = CFG3_PAR_MIF_MSECTOR_SEL_1
        hex_string = high_byte + low_byte
        number = int(hex_string, 16)
        # Convert the integer to a 16-bit binary string
        binary_string = format(number, '016b')
        boolean_list = ['1' if bool(int(bit)) else '0' for bit in reversed(binary_string)]
        cfg_mif_msector_sel = ','.join(event for event in boolean_list)
        return cfg_mif_msector_sel

    @staticmethod
    def translate_msectorkeyab_to_low_level(cfg_mif_msector_keyab):
        CFG3_PAR_MIF_MSECTOR_KEYAB_0 = None
        CFG3_PAR_MIF_MSECTOR_KEYAB_1 = None
        if cfg_mif_msector_keyab is not None:
            # cfg_mif_msector_sel ha de ser una cadena de 16 'a' o 'b' separada per comes.
            keys_list = [x.strip().lower() for x in cfg_mif_msector_keyab.split(',') if x != '']
            binary_string = ''.join(['1' if bit == 'b' else '0' for bit in reversed(keys_list)])
            number = int(binary_string, 2)
            hex_string = format(number, '04X')
            CFG3_PAR_MIF_MSECTOR_KEYAB_0 = hex_string[2:]
            CFG3_PAR_MIF_MSECTOR_KEYAB_1 = hex_string[:2]
        return CFG3_PAR_MIF_MSECTOR_KEYAB_0, CFG3_PAR_MIF_MSECTOR_KEYAB_1

    @staticmethod
    def translate_msectorkeyab_to_high_level(CFG3_PAR_MIF_MSECTOR_KEYAB_0, CFG3_PAR_MIF_MSECTOR_KEYAB_1):
        # CFG3_PAR_MIF_MSECTOR_SEL_0 / 1 han de ser cadenes hexadecimals de 2 dígits
        low_byte = CFG3_PAR_MIF_MSECTOR_KEYAB_0
        high_byte = CFG3_PAR_MIF_MSECTOR_KEYAB_1
        hex_string = high_byte + low_byte
        number = int(hex_string, 16)
        # Convert the integer to a 16-bit binary string
        binary_string = format(number, '016b')
        boolean_list = ['b' if bool(int(bit)) else 'a' for bit in reversed(binary_string)]
        cfg_mif_msector_sel = ','.join(event for event in boolean_list)
        return cfg_mif_msector_sel