# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import json
import inspect
import requests
import logging


class PostWoman:
    REQUEST_TIMEOUT = 15

    @staticmethod
    def send_get(my_url):
        try:
            result = requests.get(my_url, timeout=PostWoman.REQUEST_TIMEOUT).content.decode()
            return json.loads(result)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return None

    @staticmethod
    def send_post(my_url, dictio):
        try:
            headers = {'content-type': 'application/json'}
            result = requests.post(my_url, data=json.dumps(dictio), headers=headers, timeout=PostWoman.REQUEST_TIMEOUT).content.decode()
            return json.loads(result)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return None
