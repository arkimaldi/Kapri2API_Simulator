# (C) 2024 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
from flask_restful import Resource, reqparse
from werkzeug.security import check_password_hash
import logging

from app.messages import Messages


class SyslogRead(Resource):
    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        # Parse the arguments
        parser = reqparse.RequestParser()
        parser.add_argument('operation_key', type=str, help='operation_key')
        parser.add_argument('microservice', type=str, help='microservice')
        args = parser.parse_args()

        operation_key = args['operation_key']
        microservice = args['microservice']

        try:
            b_ret, response_systemctl, response_journalctl = self.read_syslog(operation_key, microservice)
            if b_ret:
                return {'status_code': 200, 'Result': {'response_systemctl': response_systemctl, 'response_journalctl': response_journalctl}}
            else:
                return Messages.MSG_SYSLOG_READ_ERROR
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_SYSLOG_READ_ERROR


    def read_syslog(self, operation_key, microservice):
        """
        Crida a Kapri2AssistAPI per gestionar la lectura dels logs d'un microservei donat
        """
        try:
            salt = 'e855c4bc-2294-4ce9-9842-4209f3f9d326'
            if check_password_hash(str(operation_key), str(self.kapri_app.mgr_hardware_info.get('sMAC_Address') + salt)):
                try:
                    return self.kapri_app.mgr_kapriassist.read_syslog(microservice)
                except Exception as e:
                    return False, '', ''
            else:
                logging.error(f'INFO SyslogRead. Invalid operation_key.')
                return False, '', ''
        except Exception as e:
            return False, '', ''
