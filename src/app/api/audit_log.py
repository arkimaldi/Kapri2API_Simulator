# (C) 2026 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
from flask_restful import Resource

import logging

from app.ktp_ret import KtpRet
from app.messages import Messages


class AuditLogRead(Resource):

    def __init__(self, kapri_app):
        self.kapri_app = kapri_app

    def get(self):
        try:
            uc_ret, audit_log_list = self.kapri_app.mgr_audit_logs.audit_log_read_all()
            if uc_ret == KtpRet.RET_OK:
                return {'status_code': 200, 'audit_log_list': audit_log_list}
            else:
                raise Exception('Failed ')

        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return Messages.MSG_AUDITLOG_READ_ERROR
