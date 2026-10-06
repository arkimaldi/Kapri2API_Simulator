# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
from flask_restful import Resource
from flask_restful import reqparse
import logging

from app.let_me_know_process import LetMeKnowProcess


class LetMeKnowEvent(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('msgType', type=str)
            parser.add_argument('msgArg', type=dict)
            args = parser.parse_args()

            msgType = args['msgType']
            msgArg = args['msgArg']
            result = LetMeKnowProcess.process_event(self.kapri_app, msgType, msgArg)
            return result
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return 'Error: '+ str(e)


class LetMeKnowInstruction(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('msgType', type=str)
            parser.add_argument('msgArg', type=dict)
            args = parser.parse_args()

            msgType = args['msgType']
            msgArg = args['msgArg']

            # kick semi-offline watchdog
            self.kapri_app.mgr_semi_offline.kick_keep_alive_watchdog()

            # Substituïm ins_ per ans_
            ans_do = msgType.replace('ins_', 'ans_')
            sResult, dict_answer = LetMeKnowProcess.process_instruction(self.kapri_app, msgType, msgArg)
            if sResult != 'OK':
                return sResult
            if msgArg.get('msgId') is not None:
                response = {
                    'msgType': ans_do,
                    'msgArg': {'msgId': msgArg['msgId'], **dict_answer}
                }
            else:
                response = {
                    'msgType': ans_do,
                    'msgArg': {**dict_answer}
                }
            return response
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return 'Error: ' + str(e)
