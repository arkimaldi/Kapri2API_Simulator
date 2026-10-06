# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import time
import threading
import inspect
import logging


class KTimer:

    def __init__(self, elapsed_fp):
        self.elapsed_fp = elapsed_fp
        self.lock = threading.RLock()
        self.timer_counter = 0
        timer_thread = threading.Thread(target=self.timer_thread_task, daemon=True)
        timer_thread.start()

    def set_tmo(self, timer_tmo):
        with self.lock:
            self.timer_counter = timer_tmo

    def clear_tmo(self):
        with self.lock:
            self.timer_counter = 0

    def timer_thread_task(self):
        while True:
            time.sleep(1)
            try:
                b_on_timeout = False
                with self.lock:
                    if self.timer_counter > 0:
                        self.timer_counter -= 1
                        if self.timer_counter == 0:
                            b_on_timeout = True
                if b_on_timeout:
                    self.elapsed_fp()
            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
