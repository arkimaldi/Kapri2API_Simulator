# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

from flask_restful import Resource, reqparse
import inspect
import logging

from app.messages import Messages


class UsersLogin(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('UserName', type=str, help='Username for Login')
            parser.add_argument('Password', type=str, help='Password for Login')
            args = parser.parse_args()

            user_name = args['UserName']
            user_password = args['Password']

            user_id, b_match, is_virgin = self.kapri_app.mgr_web_users.login(user_name, user_password)
            if user_id is None:
                return Messages.MSG_USER_NOT_EXISTS
            else:
                if not b_match:
                    return Messages.MSG_USERS_PASSWORDS_MISMATCH
                else:
                    return {'status_code': 200, 'idUser': user_id, 'is_virgin': is_virgin}
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_USERS_AUTHENTICATION_FAILED


class UsersLogout(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('dummy', type=str, help='dummy')
            args = parser.parse_args()
            self.kapri_app.mgr_audit_logs.audit_log_write(
                self.kapri_app.mgr_audit_logs.AUDIT_VIA_WEBADMIN, user_name=None, ip=None,
                event=self.kapri_app.mgr_audit_logs.AUDIT_EVENT_LOGOUT, ok=True
            )
            return Messages.MSG_USERS_LOGOUT_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_USERS_LOGOUT_ERROR


class UsersAdminResetPassword(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        # Parse the arguments
        parser = reqparse.RequestParser()
        parser.add_argument('operation_key', type=str, help='operation_key')
        args = parser.parse_args()

        operation_key = args['operation_key']

        try:
            b_ret = self.kapri_app.mgr_web_users.admin_reset_password(operation_key)
            self.kapri_app.mgr_audit_logs.audit_log_write(
                self.kapri_app.mgr_audit_logs.AUDIT_VIA_WEBADMIN, user_name=None, ip=None,
                event=self.kapri_app.mgr_audit_logs.AUDIT_EVENT_PWD_RECOVERY, ok=b_ret
            )
            if b_ret:
                return Messages.MSG_CHANGE_PASSWORD_OK
            else:
                return Messages.MSG_USERS_CHANGE_PASSWORD_ERROR
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_USERS_CHANGE_PASSWORD_ERROR


class UsersChangePassword(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        # Parse the arguments
        parser = reqparse.RequestParser()
        parser.add_argument('idUserLogin', type=int, help='id User')
        parser.add_argument('Old_Password', type=str, help='Password Old')
        parser.add_argument('New_Password', type=str, help='Password New')
        args = parser.parse_args()

        user_id = args['idUserLogin']
        password_old = args['Old_Password']
        password_new = args['New_Password']
        try:
            status, is_virgin = self.kapri_app.mgr_web_users.change_password(user_id, password_old, password_new)
            if status == 'NOT_FOUND':
                return Messages.MSG_USER_NOT_EXISTS
            elif status == 'OLD_PASSWORD_WRONG':
                return Messages.MSG_USERS_PASSWORD_OLD_NOT_REGISTERED
            elif status == 'FACTORY_REUSE_BLOCKED':
                return Messages.MSG_CHANGEPASSWORD_FACTORY_ERROR
            elif status == 'OK':
                self.kapri_app.mgr_audit_logs.audit_log_write(
                    self.kapri_app.mgr_audit_logs.AUDIT_VIA_WEBADMIN, user_name=None, ip=None,
                    event=self.kapri_app.mgr_audit_logs.AUDIT_EVENT_PWD_CHANGE, ok=True
                )
                return {**Messages.MSG_CHANGE_PASSWORD_OK, 'is_virgin': is_virgin}
            else:  # 'ERROR'
                return Messages.MSG_USERS_CHANGE_PASSWORD_ERROR
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_USERS_CHANGE_PASSWORD_ERROR


class UsersReadUser(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def get(self, idUser):
        try:
            dict_info_user = self.kapri_app.mgr_web_users.read_user(idUser)
            if dict_info_user is None:
                return Messages.MSG_ERROR_ACCESS_BBDD
            else:
                return {'status_code': 200, 'Result': dict_info_user}
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_ERROR_ACCESS_BBDD

