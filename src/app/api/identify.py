# (C) 2024 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
from flask_restful import Resource, reqparse
import logging

from app.messages import Messages
from app.post_woman import PostWoman

class Identify(Resource):
    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        # Parse the arguments
        parser = reqparse.RequestParser()
        parser.add_argument('operation', type=str, help='operation')
        args = parser.parse_args()

        operation = args['operation']

        try:
            b_ret = self.identify(operation)
            if b_ret:
                return Messages.MSG_IDENTIFY_OK
            else:
                return Messages.MSG_IDENTIFY_ERROR
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_IDENTIFY_ERROR


    def identify(self, operation):
        """
        Crida a Kxp2HostProAPI per gestionar el beeper
        """
        try:
            if operation == 'beep':
                sEUI64 = self.kapri_app.mgr_hardware_info.get('sEUI64')
                ucMode = 1  # 1-'on'
                ucTime_ds = 10
                params = f"/api/nodes/{sEUI64}/InOut/BuzzerOperate/0/{ucMode}/{ucTime_ds}"
                my_url = self.kapri_app.app.config['URL']['url_kxphostproapi'] + params
                result = PostWoman.send_get(my_url)
                return result.get('ucInsRet') == 0
            else:
                return False
        except Exception as e:
            return False

