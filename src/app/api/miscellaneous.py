# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
from flask_restful import Resource
import pytz
import json
import logging

from app.ktp_ret import KtpRet
from app.messages import Messages


class SwHwVersion(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def get(self):
        try:
            dict_answer = self.kapri_app.mgr_device_info.get_device_info_dict()
            uc_ret = dict_answer['ucRet']
            del dict_answer['ucRet']

            if uc_ret == KtpRet.RET_OK:
                return {'status_code': 200, **dict_answer}
            else:
                raise Exception('Failed ')
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_SW_HW_VERSION_GET_ERROR


class RtcAllTimezonesGet(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def get(self):
        try:
            uc_ret, rtc_dict = self.rtc_timezone_get()
            if uc_ret == KtpRet.RET_OK:
                return {'status_code': 200, **rtc_dict}
            else:
                raise Exception('Failed ')
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_TIMEZONES_GET_RTC_ALL_ERROR

    def rtc_timezone_get(self):
        ucRet = KtpRet.RET_OK
        rtc_dict = {'all_timezones': []}
        try:
            all_timezones = json.dumps(pytz.all_timezones)
            rtc_dict = {'all_timezones': all_timezones}
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_EXCEPTION
        finally:
            return ucRet, rtc_dict

