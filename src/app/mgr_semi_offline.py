# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import time
import inspect
import json
import threading
import queue
from datetime import datetime
from sqlalchemy import asc
import logging

from k_check import KCheck
from app.global_consts import GlobalConsts
from app.ktp_ret import KtpRet
from app.db_models import NanoConfiguration, SemiOfflineEvents
from app.extensions import db
from app.evaluator import Evaluator


class MgrSemiOffline:
    SVERSION = '1.0.0'

    def __init__(self, app, mgr_semi_offline_api_caller, mgr_semi_offline_lists, on_semi_offline_mode_enter_cb, on_semi_offline_mode_leave_cb):
        self.app = app
        self.mgr_semi_offline_api_caller = mgr_semi_offline_api_caller
        self.mgr_semi_offline_lists = mgr_semi_offline_lists
        self.on_semi_offline_mode_enter_cb = on_semi_offline_mode_enter_cb
        self.on_semi_offline_mode_leave_cb = on_semi_offline_mode_leave_cb
        #
        self.b_opened = False
        self.lock = threading.Lock()
        self.semi_offline_thread = None
        self.q_queue = queue.Queue()
        self.wdg_lock = threading.Lock()
        self.wdg_thread = None
        self.wdg_keep_alive_timer = 0
        self.semi_offline_mode_enabled = None
        self.semi_offline_keep_alive_timeout = None
        self.semi_offline_on_semi_offline_mode_enter_batch = None
        self.semi_offline_on_usrtimer_elapsed_batch = None
        self.semi_offline_on_mifare_track_batch = None
        self.semi_offline_on_ttl_track_batch = None
        self.semi_offline_on_fim_finger_batch = None
        self.semi_offline_on_sfm_finger_batch = None
        self.semi_offline_on_keyboard_echo_batch = None
        self.semi_offline_on_uart_receive_batch = None

    def start(self):
        with self.lock:
            try:
                self.b_opened = False
                nano_configuration_1_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 1).first()
                if nano_configuration_1_qry is not None:
                    self.cmd_set_terminal(
                        nano_configuration_1_qry.semi_offline_mode_enabled,
                        nano_configuration_1_qry.semi_offline_keep_alive_timeout,
                        nano_configuration_1_qry.semi_offline_on_semi_offline_mode_enter_batch,
                        nano_configuration_1_qry.semi_offline_on_usrtimer_elapsed_batch,
                        nano_configuration_1_qry.semi_offline_on_mifare_track_batch,
                        nano_configuration_1_qry.semi_offline_on_ttl_track_batch,
                        nano_configuration_1_qry.semi_offline_on_fim_finger_batch,
                        nano_configuration_1_qry.semi_offline_on_sfm_finger_batch,
                        nano_configuration_1_qry.semi_offline_on_keyboard_echo_batch,
                        nano_configuration_1_qry.semi_offline_on_uart_receive_batch
                    )
                    logging.debug('cmd_set_semioffline')
                    # posem en marxa els fils de la classe
                    if self.semi_offline_thread is None:
                        self.semi_offline_thread = threading.Thread(target=self.semi_offline_thread_task, daemon=True)
                        self.semi_offline_thread.start()
                    if self.wdg_thread is None:
                        self.wdg_thread = threading.Thread(target=self.wdg_thread_task, daemon=True)
                        self.wdg_thread.start()
                    if self.semi_offline_mode_enabled and self.semi_offline_keep_alive_timeout is not None:
                        self.b_opened = True
                        with self.wdg_lock:
                            self.wdg_keep_alive_timer = self.semi_offline_keep_alive_timeout
            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            finally:
                db.session.close()

    def cmd_set_terminal(self, semi_offline_mode_enabled, semi_offline_keep_alive_timeout,
                         semi_offline_on_semi_offline_mode_enter_batch, semi_offline_on_usrtimer_elapsed_batch,
                         semi_offline_on_mifare_track_batch,
                         semi_offline_on_ttl_track_batch, semi_offline_on_fim_finger_batch, semi_offline_on_sfm_finger_batch,
                         semi_offline_on_keyboard_echo_batch, semi_offline_on_uart_receive_batch):
        # semi_offline_mode_enabled
        try:
            self.semi_offline_mode_enabled = KCheck.booleanValue(semi_offline_mode_enabled)
        except Exception as e:
            self.semi_offline_mode_enabled = None
        #  semi_offline_keep_alive_timeout
        try:
            self.semi_offline_keep_alive_timeout = KCheck.integerInInterval(semi_offline_keep_alive_timeout, 1, 24 * 3600)
        except Exception as e:
            self.semi_offline_keep_alive_timeout = None
        # semi-offline batches
        try:
            self.semi_offline_on_semi_offline_mode_enter_batch = json.loads(semi_offline_on_semi_offline_mode_enter_batch)
        except Exception as e:
            self.semi_offline_on_semi_offline_mode_enter_batch = None
        try:
            self.semi_offline_on_usrtimer_elapsed_batch = json.loads(semi_offline_on_usrtimer_elapsed_batch)
        except Exception as e:
            self.semi_offline_on_usrtimer_elapsed_batch = None
        try:
            self.semi_offline_on_mifare_track_batch = json.loads(semi_offline_on_mifare_track_batch)
        except Exception as e:
            self.semi_offline_on_mifare_track_batch = None
        try:
            self.semi_offline_on_ttl_track_batch = json.loads(semi_offline_on_ttl_track_batch)
        except Exception as e:
            self.semi_offline_on_ttl_track_batch = None
        try:
            self.semi_offline_on_fim_finger_batch = json.loads(semi_offline_on_fim_finger_batch)
        except Exception as e:
            self.semi_offline_on_fim_finger_batch = None
        try:
            self.semi_offline_on_sfm_finger_batch = json.loads(semi_offline_on_sfm_finger_batch)
        except Exception as e:
            self.semi_offline_on_sfm_finger_batch = None
        try:
            self.semi_offline_on_keyboard_echo_batch = json.loads(semi_offline_on_keyboard_echo_batch)
        except Exception as e:
            self.semi_offline_on_keyboard_echo_batch = None
        try:
            self.semi_offline_on_uart_receive_batch = json.loads(semi_offline_on_uart_receive_batch)
        except Exception as e:
            self.semi_offline_on_uart_receive_batch = None

    def cmd_get_version(self):
        return MgrSemiOffline.SVERSION

    # -----------------------------------------------------------------------------------------------------------------

    def get_version(self):
        try:
            return self.cmd_get_version()
        except Exception as e:
            return None

    def write_event_semi_offline(self, event_dictio, instruction_dictio, response_dictio):
        try:
            # Count previ: si supera 10.000, borrarem els 1000 més antics
            count_eso = db.session.query(SemiOfflineEvents).count()
            if count_eso >= GlobalConsts.get('const_max_num_semi_offline_events_in_table'):
                eso_ordered_qry_all = db.session.query(SemiOfflineEvents).order_by(asc(SemiOfflineEvents.dt_utc)).all()
                i = 0
                max_date_allowed = datetime.strptime('1970-01-01 00:00:01', '%Y-%m-%d %H:%M:%S')
                for eso in eso_ordered_qry_all:
                    i += 1
                    if i == GlobalConsts.get('const_num_semi_offline_events_to_delete'):
                        max_date_allowed = eso.dt_utc
                        break
                db.session.query(SemiOfflineEvents).filter(SemiOfflineEvents.dt_utc < max_date_allowed).delete()
                db.session.commit()
            s_event_json = KCheck.stringLenInInterval(
                json.dumps(event_dictio),
                GlobalConsts.get('const_semi_offline_event_json_lenmin'),
                GlobalConsts.get('const_semi_offline_event_json_size')
            )
            s_instruction_json = KCheck.stringLenInInterval(
                json.dumps(instruction_dictio),
                GlobalConsts.get('const_semi_offline_event_json_lenmin'),
                GlobalConsts.get('const_semi_offline_event_json_size')
            )
            s_response_json = KCheck.stringLenInInterval(
                json.dumps(response_dictio),
                GlobalConsts.get('const_semi_offline_event_json_lenmin'),
                GlobalConsts.get('const_semi_offline_event_json_size')
            )
            dt_utc_now = datetime.utcnow()
            new_semi_offline_events = SemiOfflineEvents(event_json=s_event_json, instruction_json=s_instruction_json, response_json=s_response_json, dt_utc=dt_utc_now)
            db.session.add(new_semi_offline_events)
            db.session.commit()
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            db.session.rollback()
        finally:
            db.session.close()

    def kick_keep_alive_watchdog(self):
        if self.b_opened:
            b_notify = False
            with self.wdg_lock:
                b_was_in_semi_offline_mode = (self.wdg_keep_alive_timer == 0)
                self.wdg_keep_alive_timer = self.semi_offline_keep_alive_timeout
                if b_was_in_semi_offline_mode:
                    b_notify = True
            # notifiquem que sortim del mode semioffline:  on_semi_offline_mode_leave
            if b_notify:
                try:
                    self.on_semi_offline_mode_leave_cb()
                except Exception as e:
                    logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def is_server_alive(self):
        if self.b_opened:
            return self.wdg_keep_alive_timer > 0
        else:
            return True

    def manage_event(self, my_dictio):
        if self.b_opened:
            try:
                dictio = json.loads(json.dumps(my_dictio))
                self.q_queue.put(dictio)
            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def semi_offline_thread_task(self):
        with self.app.app_context():
            while True:
                try:
                    tx_dictio = self.q_queue.get()
                    event_type = tx_dictio['msgType']
                    if event_type == 'on_semi_offline_mode_enter':
                        rx_dictio = self.semi_offline_on_semi_offline_mode_enter_batch
                    elif event_type == 'on_usrtimer_elapsed':
                        rx_dictio = self.semi_offline_on_usrtimer_elapsed_batch
                    elif event_type == 'on_mifare_track':
                        rx_dictio = self.semi_offline_on_mifare_track_batch
                    elif event_type == 'on_ttl_track':
                        rx_dictio = self.semi_offline_on_ttl_track_batch
                    elif event_type == 'on_fim_finger':
                        rx_dictio = self.semi_offline_on_fim_finger_batch
                    elif event_type == 'on_sfm_finger':
                        rx_dictio = self.semi_offline_on_sfm_finger_batch
                    elif event_type == 'on_keyboard_echo':
                        rx_dictio = self.semi_offline_on_keyboard_echo_batch
                    elif event_type == 'on_uart_receive':
                        rx_dictio = self.semi_offline_on_uart_receive_batch
                    else:
                        rx_dictio = None
                    if rx_dictio is not None:
                        # processem el batch
                        ans_dictio = self.batch_process(tx_dictio, rx_dictio)
                        # documentem l'event que l'ha causat, el batch i la resposta del batch
                        self.write_event_semi_offline(tx_dictio, rx_dictio, ans_dictio)
                        # descartem els events que s'hagin pogut produir mentre processavem el batch
                        self.q_queue.queue.clear()
                except Exception as e:
                    logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def batch_process(self, tx_dictio, rx_dictio):
        """
        retorna
            -None:
                si rep None
                si rep una llista de batch buida
                si no ha de respondre
            - la resposta de processar el batch. El batch es la resposta a un event o a un ans_cloud_batch.
              És un json amb els camps:
                   'msgType': 'ins_semi_offline_batch'
                   'msgArg': {
                               'bReply': un booleà que indica si caldrà enviar un ans_cloud_batch al final del processament del batch
                               'listBatch': llista de instruccions
                              }
        """
        if rx_dictio is None:
            return None
        # msgType ---
        try:
            rx_msgType = rx_dictio['msgType']
            if type(rx_msgType) is not str:
                raise Exception('K_Batch_Process-Error')
            if rx_msgType != 'ins_semi_offline_batch':
                raise Exception('K_Batch_Process-Error')
        except Exception as e:
            return {'msgType': 'ans_semi_offline_batch', 'msgArg': {'ucRet': KtpRet.RET_INVALIDTYPE}}
        # msgArg ---
        try:
            rx_msgArg = rx_dictio['msgArg']
            rx_b_reply = KCheck.booleanValue(rx_msgArg.get('bReply', False))
            rx_list_batch = rx_msgArg['listBatch']
            rx_msgId = rx_msgArg.get('msgId')
            if type(rx_list_batch) is not list:
                raise Exception('K_Batch_Process-Error')
            sJson = json.dumps(rx_list_batch)
            if json.loads(sJson) != rx_list_batch:
                raise Exception('K_Batch_Process-Error')
            for elem_dict_instruction in rx_list_batch:
                if type(elem_dict_instruction) is not dict:
                    raise Exception('K_Batch_Process-Error')
                if 'msgType' not in elem_dict_instruction.keys():
                    raise Exception('K_Batch_Process-Error')
                if 'msgArg' not in elem_dict_instruction.keys():
                    raise Exception('K_Batch_Process-Error')
                if type(elem_dict_instruction['msgType']) is not str:
                    raise Exception('K_Batch_Process-Error')
                if type(elem_dict_instruction['msgArg']) is not dict:
                    raise Exception('K_Batch_Process-Error')
        except Exception as e:
            return {'msgType': 'ans_semi_offline_batch', 'msgArg': {'ucRet': KtpRet.RET_INVALIDARGUMENT}}
        # processem batch ---
        try:
            if len(rx_list_batch) == 0:
                return None
            tx_answer_list = []
            o_evaluator = Evaluator(self.app, self.mgr_semi_offline_lists, tx_dictio)
            for elem_dict_instruction in rx_list_batch:
                instruction_to_execute = o_evaluator.enter_conditioned_instruction(elem_dict_instruction)
                if instruction_to_execute:
                    elem_dict_answer = self.mgr_semi_offline_api_caller.autocall_let_me_know(instruction_to_execute)
                    o_evaluator.enter_answer(elem_dict_answer)
                else:
                    elem_dict_answer = None
                tx_answer_list.append(elem_dict_answer)
            if rx_b_reply:
                if rx_msgId is not None:
                    return {'msgType': 'ans_semi_offline_batch', 'msgArg': {'ucRet': KtpRet.RET_OK, 'msgId': rx_msgId, 'listBatch': tx_answer_list}}
                else:
                    return {'msgType': 'ans_semi_offline_batch', 'msgArg': {'ucRet': KtpRet.RET_OK, 'listBatch': tx_answer_list}}
            else:
                return None
        except Exception as e:
            if rx_msgId is not None:
                return {'msgType': 'ans_semi_offline_batch', 'msgArg': {'ucRet': KtpRet.RET_EXCEPTION, 'msgId': rx_msgId}}
            else:
                return {'msgType': 'ans_semi_offline_batch', 'msgArg': {'ucRet': KtpRet.RET_EXCEPTION}}

    def wdg_thread_task(self):
        with self.app.app_context():
            while True:
                try:
                    if self.b_opened:
                        b_notify = False
                        with self.wdg_lock:
                            if self.wdg_keep_alive_timer > 0:
                                self.wdg_keep_alive_timer -= 1
                                if self.wdg_keep_alive_timer == 0:
                                    b_notify = True
                        if b_notify:
                            try:
                                # notifiquem que entrem en mode semioffline:  on_semi_offline_mode_enter
                                self.on_semi_offline_mode_enter_cb()
                            except Exception as e:
                                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
                except Exception as e:
                    logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
                finally:
                    time.sleep(1)