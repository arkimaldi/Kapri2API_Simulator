# (C) 2024 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
from flask_restful import Resource, reqparse
from werkzeug.security import check_password_hash
import logging

from app.messages import Messages


class SshOperate(Resource):
    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        # Parse the arguments
        parser = reqparse.RequestParser()
        parser.add_argument('operation_key', type=str, help='operation_key')
        parser.add_argument('operation', type=str, help='operation')
        args = parser.parse_args()

        operation_key = args['operation_key']
        operation = args['operation']

        try:
            b_ret = self.operate_ssh(operation_key, operation)
            if b_ret:
                return Messages.MSG_SSH_OPERATE_OK
            else:
                return Messages.MSG_SSH_OPERATE_ERROR
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_SSH_OPERATE_ERROR


    def operate_ssh(self, operation_key, operation):
        """
        Crida a Kapri2AssistAPI per gestionar l'arrencada i l'aturada del servei SSH
        """
        try:
            salt = '7245d976-99a2-427b-b901-efe0a6d9e3c4'
            if check_password_hash(str(operation_key), str(self.kapri_app.mgr_hardware_info.get('sMAC_Address') + salt)):
                try:
                    if operation == 'start':
                        b_ret = self.kapri_app.mgr_kapriassist.start_ssh()
                    elif operation == 'stop':
                        b_ret = self.kapri_app.mgr_kapriassist.stop_ssh()
                    else:
                        b_ret = False
                    return b_ret
                except Exception as e:
                    return False
            else:
                logging.error(f'INFO SshOperate. Invalid operation_key.')
                return False
        except Exception as e:
            return False
