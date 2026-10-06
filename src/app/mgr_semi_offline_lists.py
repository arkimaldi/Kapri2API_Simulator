# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

"""
Aquest mòdul gestiona l'excució de les instruccions:
    {'msgType': 'ins_semi_offline_white_list_get_all', 'msgArg': {}}
    {'msgType': 'ins_semi_offline_black_list_get_all', 'msgArg': {}}
    {'msgType': 'ins_semi_offline_white_list_set_all', 'msgArg': {'semi_offline_list_of_codes': ['a', 'b', 'c']}}
    {'msgType': 'ins_semi_offline_black_list_set_all', 'msgArg': {'semi_offline_list_of_codes': ['a', 'b', 'c']}}
    {'msgType': 'ins_semi_offline_white_list_append_one', 'msgArg': {'semi_offline_list_of_codes': ['d']}}
    {'msgType': 'ins_semi_offline_black_list_append_one', 'msgArg': {'semi_offline_list_of_codes': ['d']}}
    {'msgType': 'ins_semi_offline_white_list_delete_one', 'msgArg': {'semi_offline_list_of_codes': ['d']}}
    {'msgType': 'ins_semi_offline_black_list_delete_one', 'msgArg': {'semi_offline_list_of_codes': ['d']}}
I implementa les funcions usades en el condicionament dels lots semi-offline:
    f_in_white_list()
    f_in_black_list()
"""

import inspect
from datetime import datetime
import json
import logging

from k_check import KCheck
from app.global_consts import GlobalConsts
from app.ktp_ret import KtpRet
from app.extensions import db
from app.db_models import SemiOfflineLists


class MgrSemiOfflineLists:

    def __init__(self, app):
        self.app = app

    def get_white(self, msgArg):
        return self.get_list(msgArg, 1) # 'white'

    def get_black(self, msgArg):
        return self.get_list(msgArg, 2) # 'black'


    def set_white(self, list_of_codes):
        return self.set_list(list_of_codes, 1)  # 'white'

    def set_black(self, list_of_codes):
        return self.set_list(list_of_codes, 2)  # 'black'

    def append_white(self, list_of_codes_to_append):
        return self.append_list(list_of_codes_to_append, 1) # 'white'

    def append_black(self, list_of_codes_to_append):
        return self.append_list(list_of_codes_to_append, 2) # 'black'

    def remove_white(self, list_of_codes_to_remove):
        return self.remove_list(list_of_codes_to_remove, 1) # 'white'

    def remove_black(self, list_of_codes_to_remove):
        return self.remove_list(list_of_codes_to_remove, 2) # 'black'

    def is_in_white_list(self, s_code):
        b_ok, list_of_codes = self.get_list_from_db(1)  # 'white'
        return b_ok and s_code in list_of_codes

    def is_in_black_list(self, s_code):
        b_ok, list_of_codes = self.get_list_from_db(2)  # 'black'
        return b_ok and s_code in list_of_codes

    # ---- privats ----

    # ... que processen msgArg

    def get_list(self, msgArg, list_id):
        ucRet = KtpRet.RET_FAILED
        list_of_codes = []
        try:
            b_ok, list_of_codes = self.get_list_from_db(list_id)
            if not b_ok:
                raise
            ucRet = KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_EXCEPTION
            list_of_codes = []
        finally:
            return ucRet, list_of_codes

    def set_list(self, list_of_codes, list_id):
        ucRet = KtpRet.RET_FAILED
        try:
            list_of_codes_to_set = list(set(list_of_codes))
            b_ok = self.set_list_to_db(list_id, list_of_codes_to_set)
            if not b_ok:
                raise
            ucRet = KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_EXCEPTION
        finally:
            return ucRet

    def append_list(self, list_of_codes_to_append, list_id):
        ucRet = KtpRet.RET_FAILED
        try:
            set_of_codes_to_append = set(list_of_codes_to_append)
            b_ok, list_of_codes = self.get_list_from_db(list_id)
            if not b_ok:
                raise
            set_of_codes_in_db = set(list_of_codes)
            set_of_codes_in_db.update(set_of_codes_to_append)
            list_of_codes = list(set_of_codes_in_db)
            b_ok = self.set_list_to_db(list_id, list_of_codes)
            if not b_ok:
                raise
            ucRet = KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_EXCEPTION
        finally:
            return ucRet

    def remove_list(self, list_of_codes_to_remove, list_id):
        ucRet = KtpRet.RET_FAILED
        try:
            set_of_codes_to_remove = set(list_of_codes_to_remove)
            b_ok, list_of_codes = self.get_list_from_db(list_id)
            if not b_ok:
                raise
            set_of_codes_in_db = set(list_of_codes)
            set_of_codes_in_db.difference_update(set_of_codes_to_remove)
            list_of_codes = list(set_of_codes_in_db)
            b_ok = self.set_list_to_db(list_id, list_of_codes)
            if not b_ok:
                raise
            ucRet = KtpRet.RET_OK
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            ucRet = KtpRet.RET_EXCEPTION
        finally:
            return ucRet


    # ... que accedeixen a la db i verifiquen el tipus de dades de les llistes de codis

    def get_list_from_db(self, list_id):
        b_ret = False
        list_of_codes = []
        try:
            semi_offline_lists_qry = db.session.query(SemiOfflineLists).filter(SemiOfflineLists.list_id == list_id).first()
            list_blob = semi_offline_lists_qry.list_blob
            if list_blob is None: # tolerem el null com llista buida
                list_of_codes = []
            else:
                list_of_codes = json.loads(list_blob.decode())
                list_of_codes = MgrSemiOfflineLists.check_list_of_strings(list_of_codes)
            b_ret = True
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            list_of_codes = []
        finally:
            db.session.close()
            return b_ret, list_of_codes

    def set_list_to_db(self, list_id, list_of_codes):
        b_ret = False
        try:
            list_of_codes = MgrSemiOfflineLists.check_list_of_strings(list_of_codes)
            json_list = json.dumps(list_of_codes)
            KCheck.stringLenInInterval(
                json_list,
                GlobalConsts.get('const_semi_offline_list_blob_lenmin'),
                GlobalConsts.get('const_semi_offline_list_blob_lenmax')
            )
            try:
                semi_offline_lists_qry = db.session.query(SemiOfflineLists).filter(SemiOfflineLists.list_id == list_id).first()
                semi_offline_lists_qry.list_blob = json_list.encode()
                semi_offline_lists_qry.dt_utc = datetime.utcnow()
                db.session.add(semi_offline_lists_qry)
                db.session.commit()
                b_ret = True
            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
                db.session.rollback()
            finally:
                db.session.close()
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
        finally:
            return b_ret

    @staticmethod
    def check_list_of_strings(list_of_codes):
        if not isinstance(list_of_codes, list):
            raise
        for elem in list_of_codes:
            if not isinstance(elem, str):
                raise
        return list_of_codes