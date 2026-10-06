# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
from datetime import datetime
from sqlalchemy import and_
import logging

from app.ktp_ret import KtpRet
from app.extensions import db
from app.db_models import SemiOfflineEvents


class MgrSemiOfflineEvents:

    def __init__(self, app):
        self.app = app

    def get_range(self, s_fdu, s_tdu):
        ucRet = KtpRet.RET_FAILED
        semi_offline_events_list = []
        try:
            if s_fdu is None:
                s_fdu = '1970-01-01 00:00:01'
            from_dt_utc = datetime.strptime(s_fdu, '%Y-%m-%d %H:%M:%S')
            if s_tdu is None:
                s_tdu = '2038-01-19 03:14:07'
            to_dt_utc = datetime.strptime(s_tdu, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_EXCEPTION
            return ucRet, semi_offline_events_list
        else:
            try:
                list_ddbb = list(
                    db.session.query(
                        SemiOfflineEvents.event_json, SemiOfflineEvents.instruction_json, SemiOfflineEvents.response_json, SemiOfflineEvents.dt_utc
                    ).filter(and_(
                        from_dt_utc <= SemiOfflineEvents.dt_utc, SemiOfflineEvents.dt_utc <= to_dt_utc)
                    ).order_by(
                        SemiOfflineEvents.dt_utc
                    ).all())
                for elem in list_ddbb:
                    aux = {'event_json': elem[0],
                           'instruction_json': elem[1],
                           'response_json': elem[2],
                           'dt_utc': elem[3].strftime("%Y-%m-%d %H:%M:%S")}
                    semi_offline_events_list.append(aux)
                ucRet = KtpRet.RET_OK
            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
                ucRet = KtpRet.RET_EXCEPTION
            finally:
                db.session.close()
                return ucRet, semi_offline_events_list

    def delete_range(self, s_fdu, s_tdu):
        ucRet = KtpRet.RET_FAILED
        try:
            if s_fdu is None:
                s_fdu = '1970-01-01 00:00:01'
            from_dt_utc = datetime.strptime(s_fdu, '%Y-%m-%d %H:%M:%S')
            if s_tdu is None:
                raise Exception('to_dt_utc is needed')
            to_dt_utc = datetime.strptime(s_tdu, '%Y-%m-%d %H:%M:%S')
            db.session.query(SemiOfflineEvents).filter(
                and_(from_dt_utc <= SemiOfflineEvents.dt_utc, SemiOfflineEvents.dt_utc <= to_dt_utc)).delete()
            db.session.commit()
            ucRet = KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.rollback()
            ucRet = KtpRet.RET_EXCEPTION
        finally:
            db.session.close()
            return  ucRet