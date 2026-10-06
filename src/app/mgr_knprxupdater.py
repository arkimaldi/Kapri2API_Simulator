# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import inspect
import logging

from app.post_woman import PostWoman


class MgrKnprxupdater:

    def __init__(self, app):
        self.app = app

    def get_image_version(self):
        try:
            my_url = self.app.config['URL']['url_knpupdaterrxapi'] + '/api/image_version/read'
            result = PostWoman.send_get(my_url)
            return result.get('image_version')
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return None

