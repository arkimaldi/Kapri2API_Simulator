# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import time
import logging


class MgrServicesDetector:
    DETECTION_TMO = 20

    def __init__(self, app, mgr_kapriassist, mgr_ktpterminal, mgr_jsoterminal, mgr_httpterminal):
        self.app = app
        self.mgr_kapriassist = mgr_kapriassist
        self.mgr_ktpterminal = mgr_ktpterminal
        self.mgr_jsoterminal = mgr_jsoterminal
        self.mgr_httpterminal = mgr_httpterminal
        #
        self.message = ''

    def detect(self):
        # detecció de KapriAssistAPI
        b_kapriassist_detect = False
        kapriassist_version = ''
        for i in range(MgrServicesDetector.DETECTION_TMO):
            kapriassist_version = self.mgr_kapriassist.get_version()
            if kapriassist_version is not None:
                b_kapriassist_detect = True
                break
            time.sleep(1)
        logging.info(f'MgrServicesDetector: KapriAssistAPI {f"detected with version: {kapriassist_version}" if b_kapriassist_detect else "NOT detected"}')

        # detecció KtpTerminalProAPI
        b_ktpterminal_detect = False
        ktpterminal_version = ''
        for i in range(MgrServicesDetector.DETECTION_TMO):
            ktpterminal_version = self.mgr_ktpterminal.get_version()
            if ktpterminal_version is not None:
                b_ktpterminal_detect = True
                break
            time.sleep(1)
        logging.info(f'MgrServicesDetector KtpTerminalHostProAPI {f"detected with version: {ktpterminal_version}" if b_ktpterminal_detect else "NOT detected"}')

        # detecció JsoTerminalProAPI
        b_jsoterminal_detect = False
        jsoterminal_version = ''
        for i in range(MgrServicesDetector.DETECTION_TMO):
            jsoterminal_version = self.mgr_jsoterminal.get_version()
            if jsoterminal_version is not None:
                b_jsoterminal_detect = True
                break
            time.sleep(1)
        logging.info(f'MgrServicesDetector JsoTerminalHostProAPI {f"detected with version: {jsoterminal_version}" if b_jsoterminal_detect else "NOT detected"}')

        # detecció HttpTerminalProAPI
        b_httpterminal_detect = False
        httpterminal_version = ''
        for i in range(MgrServicesDetector.DETECTION_TMO):
            httpterminal_version = self.mgr_httpterminal.get_version()
            if httpterminal_version is not None:
                b_httpterminal_detect = True
                break
            time.sleep(1)
        logging.info(f'MgrServicesDetector HttpTerminalHostProAPI {f"detected with version: {httpterminal_version}" if b_httpterminal_detect else "NOT detected"}')

        if b_kapriassist_detect and b_ktpterminal_detect and b_jsoterminal_detect and b_httpterminal_detect:
            self.message = 'Ready...'
        else:
            self.message = 'Boot incomplete !!!'

    def get_message(self):
        return self.message
