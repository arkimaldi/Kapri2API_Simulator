# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

from flask import Blueprint
from flask_restful import Api


def api_blueprint(kapri_app):
    api_bp = Blueprint('api', __name__)
    api = Api(api_bp)

    # URL per processar les instruccions procedents del host
    from app.api.let_me_know import LetMeKnowEvent, LetMeKnowInstruction
    api.add_resource(LetMeKnowEvent, '/let_me_know_event', resource_class_kwargs={'kapri_app': kapri_app})
    api.add_resource(LetMeKnowInstruction, '/let_me_know_instruction', resource_class_kwargs={'kapri_app': kapri_app})

    # URL per processar les instruccions del semi_offline_batch
    from app.api.let_me_know_semi_offline import LetMeKnowEventFromSemiOffline, LetMeKnowInstructionFromSemiOffline
    api.add_resource(LetMeKnowEventFromSemiOffline, '/let_me_know_event_from_semi_offline', resource_class_kwargs={'kapri_app': kapri_app})
    api.add_resource(LetMeKnowInstructionFromSemiOffline, '/let_me_know_instruction_from_semi_offline', resource_class_kwargs={'kapri_app': kapri_app})

    # ----- CONFIGURATION
    from app.api.config import ReadConfig, WriteFutureConfig, ApplyConfig, RollbackConfig, ConfigBackupRestore
    api.add_resource(ReadConfig, '/readconfig', resource_class_kwargs={'kapri_app': kapri_app})
    api.add_resource(WriteFutureConfig, '/writeconfig', resource_class_kwargs={'kapri_app': kapri_app})
    api.add_resource(ApplyConfig, '/applyconfig', resource_class_kwargs={'kapri_app': kapri_app})
    api.add_resource(RollbackConfig, '/rollbackconfig', resource_class_kwargs={'kapri_app': kapri_app})
    api.add_resource(ConfigBackupRestore, '/assistconfigbackuprestore', resource_class_kwargs={'kapri_app': kapri_app})

    # ---- WRITE MIFARE KEYS
    from app.api.mifare_keys import AssistWriteMifareKeys
    api.add_resource(AssistWriteMifareKeys, '/assistwritemifarekey', resource_class_kwargs={'kapri_app': kapri_app})

    # ----- VERSIONS
    from app.api.version import Version
    api.add_resource(Version, '/Version', resource_class_kwargs={'kapri_app': kapri_app})

    # ----- USERS
    from app.api.users import UsersLogin, UsersLogout, UsersAdminResetPassword, UsersChangePassword, UsersReadUser
    api.add_resource(UsersLogin, '/Users/Login', resource_class_kwargs={'kapri_app': kapri_app})
    api.add_resource(UsersLogout, '/Users/Logout', resource_class_kwargs={'kapri_app': kapri_app})
    api.add_resource(UsersAdminResetPassword, '/Users/AdminResetPassword', resource_class_kwargs={'kapri_app': kapri_app})
    api.add_resource(UsersChangePassword, '/Users/ChangePassword', resource_class_kwargs={'kapri_app': kapri_app})
    api.add_resource(UsersReadUser, '/Users/Read/<int:idUser>', resource_class_kwargs={'kapri_app': kapri_app})

    # ---- MISCELLANEOUS
    from app.api.miscellaneous import SwHwVersion, RtcAllTimezonesGet
    api.add_resource(SwHwVersion, '/sw_hw_version', resource_class_kwargs={'kapri_app': kapri_app})
    api.add_resource(RtcAllTimezonesGet, '/rtc_all_timezones_get', resource_class_kwargs={'kapri_app': kapri_app})

    # ---- IMAGE MANAGEMENT
    from app.api.images import ScreenImagesList, ScreenimagesView, ScreenImagesDelete, ScreenImagesStore
    api.add_resource(ScreenImagesList, '/screen_images_list', resource_class_kwargs={'kapri_app': kapri_app})
    api.add_resource(ScreenimagesView, '/screen_images_view/<string:sImgName>', resource_class_kwargs={'kapri_app': kapri_app})
    api.add_resource(ScreenImagesDelete, '/screen_images_delete/<string:sImgName>', resource_class_kwargs={'kapri_app': kapri_app})
    api.add_resource(ScreenImagesStore, '/screen_images_store', resource_class_kwargs={'kapri_app': kapri_app})

    # ---- SYSLOG
    from app.api.syslog import SyslogRead
    api.add_resource(SyslogRead, '/Syslog/Read', resource_class_kwargs={'kapri_app': kapri_app})

    # ---- SSH
    from app.api.ssh import SshOperate
    api.add_resource(SshOperate, '/Ssh/Operate', resource_class_kwargs={'kapri_app': kapri_app})

    # ---- IDENTIFY
    from app.api.identify import Identify
    api.add_resource(Identify, '/Identify', resource_class_kwargs={'kapri_app': kapri_app})

    # ---- AUDIT LOGS
    from app.api.audit_log import AuditLogRead
    api.add_resource(AuditLogRead, '/Auditlog/Read', resource_class_kwargs={'kapri_app': kapri_app})

    # ---- CFG FACTORY RESET
    from app.api.config import ConfigFactoryReset
    api.add_resource(ConfigFactoryReset, '/configfactoryreset', resource_class_kwargs={'kapri_app': kapri_app})

    return api_bp
