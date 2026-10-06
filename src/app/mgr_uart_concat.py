# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import queue
import threading
import inspect
import logging


class MgrUartConcat:

    DATA_LEN_THRESHOLD_TO_TRIGGER_EVENT = 900
    TMO_TO_TRIGGER_EVENT = 0.25

    def __init__(self, app, on_concat_data_cb):
        self.app = app
        self.on_concat_data_cb = on_concat_data_cb
        #
        self.concat_queue = queue.Queue()
        self.concat_thread = None

    def start(self):
        self.concat_thread = threading.Thread(target=self.concat_thread_task, daemon=True)
        self.concat_thread.start()

    def on_uart_received(self, s_data):
        if self.concat_thread is not None:
            self.concat_queue.put(s_data)

    def concat_thread_task(self):
        s_concat_data = ''
        while True:
            try:
                if len(s_concat_data) == 0:
                    s_concat_data += self.concat_queue.get()
                else:
                    try:
                        s_concat_data += self.concat_queue.get(block=True, timeout=MgrUartConcat.TMO_TO_TRIGGER_EVENT)
                    except Exception as e:
                        # generem event per tmo
                        self.raise_event(s_concat_data)
                        s_concat_data = ''
                    else:
                        if len(s_concat_data) >= MgrUartConcat.DATA_LEN_THRESHOLD_TO_TRIGGER_EVENT:
                            # generem event per longitud
                            self.raise_event(s_concat_data)
                            s_concat_data = ''
            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
                s_concat_data = ''

    def raise_event(self, s_data):   # data es un string immutable, no cal copiar-lo per passar-lo al nou fil
        event_raiser_thread = threading.Thread(target=self.thread_event_raiser_task, args=(s_data,))
        event_raiser_thread.daemon = True
        event_raiser_thread.start()

    def thread_event_raiser_task(self, s_data):
        try:
            self.on_concat_data_cb(s_data)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
