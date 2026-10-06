# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import time
import inspect
import json
import threading
import queue
import logging

from k_check import KCheck
from app.ktp_ret import KtpRet
from app.db_models import NanoConfiguration
from app.extensions import db
from app.post_woman import PostWoman


class MgrCloudterminal:
    SVERSION = '1.0.0'

    def __init__(self, app, mgr_hardware_info, mgr_guispy):
        self.app = app
        self.mgr_hardware_info = mgr_hardware_info
        self.mgr_guispy = mgr_guispy
        #
        self.b_opened = False
        self.s_cloud_remote_server_url = ''
        self.s_cloud_remote_server_token = ''
        self.l_cloud_allowed_events = []
        self.i_cloud_keep_alive_timeout = 0
        self.i_cloud_busy_relay = -1
        self.lock = threading.Lock()
        self.cloud_thread = None
        self.q_queue = queue.Queue()

    def start(self):
        with self.lock:
            try:
                self.b_opened = False
                nano_configuration_1_qry = db.session.query(NanoConfiguration).filter(NanoConfiguration.id == 1).first()
                if nano_configuration_1_qry is not None:
                    self.cmd_set_terminal(
                        nano_configuration_1_qry.cloud_remote_server_url,
                        nano_configuration_1_qry.cloud_remote_server_token,
                        nano_configuration_1_qry.cloud_allowed_events,
                        nano_configuration_1_qry.cloud_keep_alive_timeout,
                        nano_configuration_1_qry.cloud_busy_relay
                    )
                    logging.debug('cmd_set_terminal')
                    # posem en marxa el fil de la classe
                    if self.cloud_thread is None:
                        self.cloud_thread = threading.Thread(target=self.cloud_thread_task, daemon=True)
                        self.cloud_thread.start()
                    self.b_opened = nano_configuration_1_qry.cloud_interface
            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            finally:
                db.session.close()

    def cmd_set_terminal(self, s_cloud_remote_server_url, s_cloud_remote_server_token, s_cloud_allowed_events, i_cloud_keep_alive_timeout, i_cloud_busy_relay):
        self.s_cloud_remote_server_url = s_cloud_remote_server_url
        self.s_cloud_remote_server_token = s_cloud_remote_server_token
        try:
            self.l_cloud_allowed_events = [x.strip() for x in s_cloud_allowed_events.split(',') if x != '']
        except Exception as e:
            self.l_cloud_allowed_events = []
        self.i_cloud_keep_alive_timeout = i_cloud_keep_alive_timeout
        self.i_cloud_busy_relay = i_cloud_busy_relay

    def cmd_get_version(self):
        return MgrCloudterminal.SVERSION

    def get_version(self):
        try:
            return self.cmd_get_version()
        except Exception as e:
            return None

    # -----------------------------------------------------------------------------------------------------------------

    def send_and_receive(self, my_dictio):
        # Farem servir aquesta funció per totes les crides API al Cloud
        try:
            my_url = self.s_cloud_remote_server_url
            result = PostWoman.send_post(my_url, my_dictio)
            return result
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return None

    def autocall_let_me_know(self, my_dictio):
        # Farem servir aquesta funció per totes les crides API al LetMeKnow del propi Kapri2API
        # per tal de processar les instruccions que venen en batch com a resposta d'events o a batchos anteriors
        try:
            api_port = self.app.config['API']['api_port']
            my_url = f'http://127.0.0.1:{api_port}/api/let_me_know_instruction'
            result = PostWoman.send_post(my_url, my_dictio)
            return result
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return {'Error': str(e)}

    def manage_event(self, my_dictio):
        try:
            if self.b_opened:
                dictio = json.loads(json.dumps(my_dictio))
                if dictio['msgType'] in self.l_cloud_allowed_events:
                    self.q_queue.put(dictio)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def cloud_thread_task(self):
        with self.app.app_context():
            while True:
                try:
                    if self.b_opened:
                        # desencuem events
                        tx_dictio = None
                        loop_count = 0
                        b_exit_loop = False
                        while not b_exit_loop:
                            try:
                                tx_dictio = self.q_queue.get(block=True, timeout=1)
                            except Exception as e:
                                # timeout
                                if not self.b_opened:
                                    tx_dictio = None
                                    b_exit_loop = True
                                elif self.i_cloud_keep_alive_timeout > 0 and 'on_cloud_keep_alive' in self.l_cloud_allowed_events:
                                    # keep alive activat
                                    loop_count += 1
                                    if loop_count >= self.i_cloud_keep_alive_timeout:
                                        tx_dictio = {'msgType': 'on_cloud_keep_alive', 'msgArg': {}}
                                        b_exit_loop = True
                            else:
                                if not self.b_opened:
                                    tx_dictio = None
                                b_exit_loop = True      # si CLOUD activat, tx_dictio conté l'event desencuat
                        # processem events desencuats
                        if tx_dictio is not None:
                            triggered_by_gui_event = MgrCloudterminal.is_gui_event(tx_dictio)
                            while tx_dictio is not None:
                                # afegim sEUI64 i sToken a tot el que puja cap al cloud
                                tx_dictio['msgArg']['sEUI64'] = self.mgr_hardware_info.get('sEUI64')
                                tx_dictio['msgArg']['sToken'] = self.s_cloud_remote_server_token
                                # enviem un event o un keep alive i obtenim el batch d'instruccions a executar en la resposta
                                if triggered_by_gui_event:
                                    self.mgr_guispy.show_loading_icon()
                                    self.set_relay_busy_on()
                                rx_dictio = self.send_and_receive(tx_dictio)
                                if triggered_by_gui_event:
                                    self.mgr_guispy.hide_loading_icon()
                                # processem el batch
                                tx_dictio = self.batch_process(rx_dictio)
                                if triggered_by_gui_event:
                                    self.set_relay_busy_off()
                            # descartem els events de la "gui" anteriors que s'hagin pogut produir mentre processàvem el batch
                            if triggered_by_gui_event:
                                self.discard_enqueued_gui_events()
                    else:
                        self.q_queue.queue.clear()
                        time.sleep(1)
                except Exception as e:
                    logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def batch_process(self, rx_dictio):
        """
        retorna
            -None:
                si rep None
                si rep una llista de batch buida
                si no ha de respondre
            - la resposta de processar el batch. El batch es la resposta a un event o a un ans_cloud_batch.
              És un json amb els camps:
                   'msgType': 'ins_cloud_batch'
                   'msgArg': {
                               'bReply': un booleà que indica si caldrà enviar un ans_cloud_batch al final del processament del batch
                               'listBatch': llista d' instruccions
                              }
        """
        if rx_dictio is None:
            return None
        # msgType ---
        try:
            rx_msgType = rx_dictio['msgType']
            if type(rx_msgType) is not str:
                raise Exception('K_Batch_Process-Error')
            if rx_msgType != 'ins_cloud_batch':
                raise Exception('K_Batch_Process-Error')
        except Exception as e:
            return {'msgType': 'ans_cloud_batch', 'msgArg': {'ucRet': KtpRet.RET_INVALIDTYPE}}
        # msgArg ---
        try:
            rx_msgArg = rx_dictio['msgArg']
            rx_b_reply = KCheck.booleanValue(rx_msgArg['bReply'])
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
            return {'msgType': 'ans_cloud_batch', 'msgArg': {'ucRet': KtpRet.RET_INVALIDARGUMENT}}
        # processem batch ---
        try:
            if len(rx_list_batch) == 0:
                return None
            tx_answer_list = []
            for elem_dict_instruction in rx_list_batch:
                elem_dict_answer = self.autocall_let_me_know(elem_dict_instruction)
                tx_answer_list.append(elem_dict_answer)
            if rx_b_reply:
                if rx_msgId is not None:
                    return {'msgType': 'ans_cloud_batch', 'msgArg': {'ucRet': KtpRet.RET_OK, 'msgId': rx_msgId, 'listBatch': tx_answer_list}}
                else:
                    return {'msgType': 'ans_cloud_batch', 'msgArg': {'ucRet': KtpRet.RET_OK, 'listBatch': tx_answer_list}}
            else:
                return None
        except Exception as e:
            if rx_msgId is not None:
                return {'msgType': 'ans_cloud_batch', 'msgArg': {'ucRet': KtpRet.RET_EXCEPTION, 'msgId': rx_msgId}}
            else:
                return {'msgType': 'ans_cloud_batch', 'msgArg': {'ucRet': KtpRet.RET_EXCEPTION}}

    @staticmethod
    def is_gui_event(tx_dictio):
        if tx_dictio['msgType'] == 'on_sfm_finger':
            # l'event d'inici d'identificació del mòdul SFM no es considera gui_event per tal de no esborrar el de final d'identificació.
            b_ret = tx_dictio['msgArg'].get('ucSfmResult') != 98  # 98: inici de identificació
        else:
            b_ret = tx_dictio['msgType'] in [
                'on_mifare_track',
                'on_ttl_track',
                'on_fim_finger',
                'on_keyboard_echo',
                'on_uart_receive'
            ]
        return b_ret

    def discard_enqueued_gui_events(self):
        # create a new empty queue
        new_queue = queue.Queue()
        # iterate through the elements in the CloudTerminal.q_queue
        while not self.q_queue.empty():
            element = self.q_queue.get()
            # if the element is not a "gui" event
            if not MgrCloudterminal.is_gui_event(element):
                new_queue.put(element)
        # replace the original queue with the new queue
        self.q_queue.queue.clear()
        while not new_queue.empty():
            self.q_queue.put(new_queue.get())

    def set_relay_busy_on(self):
        if self.i_cloud_busy_relay > -1:
            self.autocall_let_me_know(
                {
                    'msgType': 'ins_inout_relay_operate',
                    'msgArg': {
                        'sPosition': 'main',
                        'ucRelayNum': self.i_cloud_busy_relay,
                        'ucTime_ds': 255
                    }
                }
            )

    def set_relay_busy_off(self):
        if self.i_cloud_busy_relay > -1:
            self.autocall_let_me_know(
                {
                    'msgType': 'ins_inout_relay_switch_off',
                    'msgArg': {
                        'sPosition': 'main',
                        'ucRelayNum': self.i_cloud_busy_relay
                    }
                }
            )