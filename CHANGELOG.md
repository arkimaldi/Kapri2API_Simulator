# Històric

## NOTA: informar la versió a GlobalConsts.py a la key 'const_my_version'

## 20/07/2026 ver 2.0.7
    · Pel compliment del CRA referent al canvi del password de fàbrica, afegim:
        - is_virgin
        - AuditLogs
    · Afegim nous paràmetres a OPTSEL
    · Afegim cleanup_orphaned_alembic_tmp_tables()

    Publicació 27/07/2026

## 19/06/2026 ver 2.0.6
    · Afegim paràmetres cfg_mif_host_fe i aux_mif_host_fe

    Publicació 19/06/2026

## 25/05/2026 ver 2.0.5
    · Corregim bug sobre les callbacks on_semi_offline_mode_enter_cb i on_semi_offline_mode_leave_cb
    · Afegim mòdul OPTSEL

## 04/05/2026 ver 2.0.4
    · Afegim suport del teclat R4x4

## 30/01/2026 ver 2.0.3
    · Convertim UdpDiscovery de unicast a broadcast

## 30/10/2025 VER 2.0.2
    · Canviem el directori de l'executable de /usr/sbin a /opt/<APPLICATION_NAME>
    · Afegim menu d'incidències al kyb_mgr
    · Afegim seqüència llarga a guispy per funcionament amb kyb_mgr
    · Afegim paràmetre de configuració cloud_busy_relay
    · Afegim f_trim() i parse_dqmini() a Evaluator

## 20/10/2025 VER 2.0.1
    · Pinejem versió rchardet a Dockerfile
    · Actualitzem versions artifacts
    · Reduïm timeout de 30  a 15 a totes les crides requests.get/post     

## 25/05/2023 ver 2.0.0
    -Partim de KapriAPI ver 1.3.1

    -Repercutim canvis de KapriAPI ver 1.3.2
        Ampliem el rang de longituds de password de [4, 10] a [4, 15]
        Corregim bug a check_cloud_allowed_events()
    
    -Repercutim canvis de KapriAPI ver 1.3.3
        Afegim el camp oExtra a l'event on_keyboard_echo, només subcamp lblmgr

    -Repercutim canvis de KapriAPI ver 1.3.4
        Corregim un bug que impedia l'emissió de l'event final de identificació biomètrica del modul SFM 
        mentre es processava l'event d'inici de la identificació.

    -Repercutim els canvis de KapriAPI ver 1.4.0
        Afegim el punt dins de la llista de caràcters admesos en les contrasenyes
        Afegim URLs per gestionar slg(=forgot password), pwd, ssh des del KapriAssistAPI
        Afegim sMAC_AddressWLAN
        Afegim instrucció ins_cpu_scan_wifi
        Afegim control de les extensions de les imatges desades
        Afegim api/Identify
        Afegim reintents en la detecció de la MAC 
        Afegim personalitzacions d'avaluació:
            - 'f_qr_b4a63890ed97' Prototipus per NubApp
            - 'f_qr_f84399dbec2e' Validador prefix Virtuagym
        A KybMgr:
        - establim un mínim operatiu per a KEYBOARD_TIMEOUT de 3
        - hi afegim el paràmetre 'prompt_timeout' entre 5 i 60 defecte 10, per controlar el temps màxim en edició
          en code_selection = 'prompt'

    -Repercutim els canvis de KapriAPI ver 1.4.1
        Corregim bug en la validació de les imatges en base64 dels html.

    -Repercutim els canvis de KapriAPI ver 1.4.2
        Afegim instrucció ins_cloud_semi_offline
        Afegim senyalització de l'emissió d'un post en protocol CLOUD
        Invertim l'ordre de prioritats dels paràmetres de ins_cloud_sleep

    -Repercutim els canvis de KapriAPI ver 1.4.3
         Afegim mode de lectura mifare multisector.
            - cfg_mif_mode: afegim valor 'multisector', 'reversed_atqa_uid', 'mad_one_block', 'mad_three_blocks'
            - cfg_mif_msector_sel
            - cfg_mif_msector_keyab

    Publicació 11/04/2025
