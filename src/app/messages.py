# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

class Messages:

    # Missatges de retorn controlat
    # -- Users
    MSG_USERS_LOGOUT_OK = {'status_code': 200, 'Message': '--KapriAPI_message-- Logout'}
    MSG_CHANGE_PASSWORD_OK = {'status_code': 200, 'Message': '--KapriAPI_message-- Password changed successfully'}

    # =================================
    # Missatges d'excepcions (3001...)
    # =================================

    # -- Control Sessió Usuari
    MSG_USER_NOT_EXISTS = {'status_code': 1001, 'Message': '--KapriAPI_message-- Non-existent user'}
    MSG_USERS_PASSWORDS_MISMATCH = {'status_code': 1002, 'Message': '--KapriAPI_message-- Passwords do not match'}

    # -- Generals
    MSG_ERROR_ACCESS_BBDD = {'status_code': 3500, 'Message': '--KapriAPI_message-- An error has occurred when accessing the database'}

    # -- Users
    MSG_USERS_AUTHENTICATION_FAILED = {'status_code': 3001, 'Message': '--KapriAPI_message-- Unable to authenticate'}
    MSG_USERS_LOGOUT_ERROR = {'status_code': 3002, 'Message': '--KapriAPI_message-- Logout error'}
    MSG_USERS_PASSWORD_OLD_NOT_REGISTERED = {'status_code': 3005, 'Message': '--KapriAPI_message-- Incorrect password'}
    MSG_CHANGEPASSWORD_FACTORY_ERROR = {'status_code':3010,'Message': '--KapriAPI_message-- New password must be different from the factory default.'}
    MSG_USERS_CHANGE_PASSWORD_ERROR = {'status_code': 3011 , 'Message': '--KapriAPI_message-- An error has occurred. Password not modified'}

    # -- Write Nanopi Config
    MSG_CONFIG_WRITE_FUTURE_OK = {'status_code': 200, 'Message': '--KapriAPI_message-- Configuration successfully updated'}
    MSG_CONFIG_WRITE_FUTURE_ERROR = {'status_code': 3100, 'Message': '--KapriAPI_message-- Invalid configuration parameters'}
    MSG_CONFIG_WRITE_FUTURE_ERROR_DB = {'status_code': 3101, 'Message': '--KapriAPI_message-- Problem writing configuration to database'}
    MSG_CONFIG_APPLY_CURRENT_OK  = {'status_code': 200, 'Message': '--KapriAPI_message-- Settings applied correctly'}
    MSG_CONFIG_APPLY_CURRENT_ERROR_DB = {'status_code': 3102, 'Message': '--KapriAPI_message-- Problem applying the configuration in the database'}
    MSG_CONFIG_APPLY_CURRENT_ERROR = {'status_code': 3103, 'Message': '--KapriAPI_message-- Problem applying settings'}
    MSG_CONFIG_ROLLBACK_CURRENT_OK = {'status_code': 200, 'Message': '--KapriAPI_message-- Settings reverted correctly'}
    MSG_CONFIG_ROLLBACK_CURRENT_ERROR = {'status_code': 3104, 'Message': '--KapriAPI_message-- Problem reverting settings'}

    # -- Backup/Restore Config
    MSG_CONFIG_BACKUP_OK = {'status_code': 200, 'Message': '--KapriAPI_message-- Backup successful'}
    MSG_CONFIG_RESTORE_OK = {'status_code': 200, 'Message': '--KapriAPI_message-- Restore successful'}
    MSG_CONFIG_BACKUP_RESTORE_ERROR = {'status_code': 3201, 'Message': '--KapriAPI_message-- Backup/Restore operation problem'}

    # -- Mifare Keys
    MSG_MIFARE_KEYS_WRITE_OK  = {'status_code': 200, 'Message': '--KapriAPI_message-- Mifare keys updated successfully'}
    MSG_MIFARE_KEYS_WRITE_ERROR = {'status_code': 3301, 'Message': '--KapriAPI_message-- Problem writing Mifare Keys'}

    # -- Sw/Hw Version
    MSG_SW_HW_VERSION_GET_ERROR = {'status_code': 3401, 'Message': '--KapriAPI_message-- Problem getting information about Software and Hardware'}

    # -- Timezones
    MSG_TIMEZONES_GET_RTC_ALL_ERROR  = {'status_code': 3501, 'Message': '--KapriAPI_message-- Problem getting Timezones'}

    # -- Screen Images
    MSG_SCREEN_IMAGES_LIST_ERROR = {'status_code': 3601, 'Message': '--KapriAPI_message-- Problem getting the list of stored images'}
    MSG_SCREEN_IMAGES_VIEW_ERROR = {'status_code': 3602, 'Message': '--KapriAPI_message-- Problem getting the image view'}
    MSG_SCREEN_IMAGES_DELETE_ERROR = {'status_code': 3603, 'Message': '--KapriAPI_message-- Problem erasing the image'}
    MSG_SCREEN_IMAGES_ADD_ERROR = {'status_code': 3604, 'Message': '--KapriAPI_message-- Problem saving the image'}

    # -- Syslog
    MSG_SYSLOG_READ_ERROR = {'status_code': 3701, 'Message': '--KapriAPI_message-- Problem reading Syslog'}

    # -- Ssh
    MSG_SSH_OPERATE_OK = {'status_code': 200, 'Message': '--KapriAPI_message-- SSH successfully operated'}
    MSG_SSH_OPERATE_ERROR = {'status_code': 3801, 'Message': '--KapriAPI_message-- Problem operating SSH'}

    # -- Identify
    MSG_IDENTIFY_OK = {'status_code': 200, 'Message': '--KapriAPI_message-- Device successfully identified'}
    MSG_IDENTIFY_ERROR = {'status_code': 3901, 'Message': '--KapriAPI_message-- Problem identifying the device'}

    # -- Audit Log
    MSG_AUDITLOG_READ_ERROR = {'status_code': 4001, 'Message': '--KapriAPI_message-- Problem reading Auditlog'}

    # -- Reset Factory Config
    MSG_FACTORY_RESET_OK = {'status_code':200, 'Message': '--KapriAPI_message-- Factory Reset successful'}
    MSG_FACTORY_RESET_ERROR = {'status_code':4101, 'Message': '--KapriAPI_message-- Factory Reset operation problem'}