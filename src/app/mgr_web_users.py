# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

from werkzeug.security import generate_password_hash, check_password_hash
import inspect
import time
import logging

from k_check import KCheck
from app.ktp_ret import KtpRet
from app.extensions import db
from app.db_models import Users
from app.utilities import Utils


class MgrWebUsers:
    PASSWORD_LEN_MIN = 4
    PASSWORD_LEN_MAX = 15
    FACTORY_USER = 'admin'
    FACTORY_PASSWORD = 'admin'

    def __init__(self, app, mgr_hardware_info, mgr_audit_logs):
        self.app = app
        self.mgr_hardware_info = mgr_hardware_info
        self.mgr_audit_logs = mgr_audit_logs
        #
        self.failed_login_count = 0

    def login(self, user_name, user_password):
        """
        :param user_name:
        :param user_password:
        :return: user_id, b_match

        Implementa el login al WebAdmin
        """
        user_name = user_name.strip().lower()
        user_password = user_password.strip()
        user_qry = db.session.query(Users).filter_by(user_name=user_name).first()
        if user_qry is not None:
            if check_password_hash(str(user_qry.user_password_hash), user_password):
                is_virgin = user_qry.is_virgin
                db.session.close()
                self.reset_failed_login_count()
                self.mgr_audit_logs.audit_log_write(
                    self.mgr_audit_logs.AUDIT_VIA_WEBADMIN, user_name=user_name, ip=None,
                    event=self.mgr_audit_logs.AUDIT_EVENT_LOGIN, ok=True
                )
                return user_qry.id, True, is_virgin
            else:
                db.session.close()
                self.delay_failed_login()
                self.mgr_audit_logs.audit_log_write(
                    self.mgr_audit_logs.AUDIT_VIA_WEBADMIN, user_name=user_name, ip=None,
                    event=self.mgr_audit_logs.AUDIT_EVENT_LOGIN, ok=False
                )
                return user_qry.id, False, True
        else:
            db.session.close()
            self.delay_failed_login()
            self.mgr_audit_logs.audit_log_write(
                self.mgr_audit_logs.AUDIT_VIA_WEBADMIN, user_name=user_name, ip=None,
                event=self.mgr_audit_logs.AUDIT_EVENT_LOGIN, ok=False
            )
            return None, False, True

    def reset_failed_login_count(self):
        self.failed_login_count = 0

    def delay_failed_login(self):
        self.failed_login_count += 1
        time.sleep(self.login_failure_delay())

    def login_failure_delay(self):
        if self.failed_login_count <= 3:
            return 0
        if self.failed_login_count <= 5:
            return 2
        if self.failed_login_count <= 7:
            return 5
        return 10

    def admin_reset_password(self, operation_key):
        """
        Implementa el reset de la password de l'admin des del WebAdmin
        La operation key és una operació sobre la MAC eth0
        """
        try:
            salt = '9e04feaf-da41-41b8-808a-dbad555de7ed'
            if check_password_hash(str(operation_key), str(self.mgr_hardware_info.get('sMAC_Address') + salt)):
                return self.reset_factory_credentials()
            else:
                logging.error(f'INFO UsersAdminResetPassword. Invalid operation_key.')
                return False
        except Exception as e:
            return False

    def change_password(self, user_id, password_old, password_new):
        """
        :param user_id:
        :param password_old:
        :param password_new:
        :return: user_name, b_changed

        Implementa el canvi de password des del WebAdmin
        """
        try:
            password_old = password_old.strip()
            password_new = password_new.strip()
            KCheck.stringLenInInterval(password_new, MgrWebUsers.PASSWORD_LEN_MIN, MgrWebUsers.PASSWORD_LEN_MAX)
            if not KCheck.validate_charset_for_password(password_new):
                raise

            users_qry = db.session.query(Users).filter_by(id=user_id).first()
            if users_qry is None:
                db.session.close()
                return 'NOT_FOUND', True

            old_is_virgin = users_qry.is_virgin
            if not check_password_hash(str(users_qry.user_password_hash), password_old):
                db.session.close()
                return 'OLD_PASSWORD_WRONG', old_is_virgin

            if old_is_virgin and password_new == MgrWebUsers.FACTORY_PASSWORD:
                db.session.close()
                return 'FACTORY_REUSE_BLOCKED', old_is_virgin
            # actualitzar password i is_virgin
            users_qry.user_password_hash = generate_password_hash(password_new, method='pbkdf2:sha256')
            new_is_virgin = False if (old_is_virgin and password_new != MgrWebUsers.FACTORY_PASSWORD) else old_is_virgin
            users_qry.is_virgin = new_is_virgin
            db.session.commit()
            db.session.close()
            return 'OK', new_is_virgin
        except Exception as e:
            db.session.close()
            return 'ERROR', True

    def set_credentials(self, user_name, password_old, password_new):
        """
        Aquest procediment implementa la instrucció 'ins_web_credentials_set' pensada per ser usada des del KapriCloudMainAPI
        per securitzar/dessecuritzas l'accés al WebApp del Kapri. Com que la WebApp admet únicament l'usuari 'admin',
        aquesta instrucció només permet canviar la password d'aquest usuari. Com a passwords antigues, admet password_old
        o la pròpia password_new que es vol fixar. D'aquesta manera, si el cloud reintenta la instrucció respondrà ok.
        """
        ucRet = KtpRet.RET_FAILED
        try:
            try:
                user_name = user_name.strip().lower()
                password_old = password_old.strip()
                password_new = password_new.strip()
                KCheck.stringLenInInterval(password_new, MgrWebUsers.PASSWORD_LEN_MIN, MgrWebUsers.PASSWORD_LEN_MAX)
                if user_name != MgrWebUsers.FACTORY_USER:
                    raise
                if not KCheck.validate_charset_for_password(password_new):
                    raise
            except Exception as e:
                ucRet = KtpRet.RET_INVALIDARGUMENT
            else:
                users_qry = db.session.query(Users).filter_by(user_name=user_name).first()
                if users_qry is not None:
                    if check_password_hash(str(users_qry.user_password_hash), password_new):
                        ucRet = KtpRet.RET_OK
                    else:
                        if check_password_hash(str(users_qry.user_password_hash), password_old):
                            users_qry.user_password_hash = generate_password_hash(password_new, method='pbkdf2:sha256')
                            db.session.commit()
                            ucRet = KtpRet.RET_OK
        except Exception as e:
            db.session.rollback()
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_EXCEPTION
        finally:
            db.session.close()
            return ucRet

    def reset_factory_credentials(self):
        """
        Restableix l'usuari 'admin' del WebApp a la password de fàbrica i marca is_virgin com True.
        Usat tant per la recuperació de password (AdminResetPassword) com pel Factory Reset (CRA).
        """
        b_ret = False
        try:
            users_qry = db.session.query(Users).filter_by(user_name=MgrWebUsers.FACTORY_USER).first()
            if users_qry is not None:
                users_qry.user_password_hash = generate_password_hash(MgrWebUsers.FACTORY_PASSWORD, method='pbkdf2:sha256')
                users_qry.is_virgin = True
                db.session.commit()
                b_ret = True
        except Exception as e:
            db.session.rollback()
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            b_ret = False
        finally:
            db.session.close()
            return b_ret

    def read_user(self, user_id):
        try:
            users_qry = db.session.query(Users).filter(Users.id == user_id).one()
            dict_info_user = Utils.get_qry_dict(users_qry)
            db.session.close()
            return dict_info_user
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.close()
            return None